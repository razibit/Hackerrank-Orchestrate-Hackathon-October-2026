from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .data import maybe_instant, parse_instant
from .identity import FIELD_KIND, IdentityResolver, normalize_alias
from .model import ModelCallError, classify_observations, classify_policy_conditions
from .policy import PolicyResolutionError, PolicyRule, model_policy_payload, required_treatment
from .types import AuditResult, CaseIdentity, Observation, observation_to_public_dict


class AuditBlocked(RuntimeError):
    """A material fact is unresolved; no submission row may be emitted."""


@dataclass(frozen=True)
class ClassifiedFact:
    observation: Observation
    classification: dict[str, Any]
    system_id: str
    resource_id: str

    @property
    def group_key(self) -> tuple[str, str, str, str]:
        return (
            self.system_id,
            self.resource_id,
            self.observation.scope_id or "default",
            str(self.classification["category"]),
        )


@dataclass(frozen=True)
class CurrentFact:
    fact: ClassifiedFact
    state: str
    identifiers_exposed: str
    policy_condition: str
    evidence_id: str


_STABLE_ID_FIELDS = {
    "user_id", "subject_id", "subject_reference", "customer_reference",
    "subject_ref", "subject_key", "user_ref", "owner_ref", "customer_ref",
    "customer_id", "owner_user_id", "principal_id", "identity_id",
}
_EMPTY_REFERENCE_VALUES = {"", "null", "none", "n/a", "na"}
_SUPPORT_POLICY_FIELDS = {
    "message", "message_body", "message_excerpt", "message_text", "content_text",
    "conversation_text", "thread_text", "body_text", "shared_context",
    "contains_shared_context", "conversation_has_shared_context",
    "contains_customer_context", "contains_agent_context", "contains_order_context",
}
_EXPLICIT_ALIAS_FIELDS = {
    "email", "email_address", "requester_email", "owner_email", "customer_email",
    "phone", "phone_number", "mobile", "email_hash", "email_sha256", "hashed_email",
}

_OPERATION_RANK = {
    "REPORT_REMAINING_RECORD": 0,
    "REPORT_EXPOSED_PII": 1,
    "REPORT_ACTIVE_DATA_FLOW": 2,
    "REPORT_RESTORE_RISK": 3,
    "DISABLE_DATA_FLOW": 4,
    "BLOCK_RESTORE": 5,
    "DELETE_RECORD": 6,
    "REDACT_RECORD": 7,
    "ANONYMIZE_RECORD": 8,
    "VERIFY_RECORD_ABSENT": 9,
    "VERIFY_RECORD_PRESENT": 10,
    "VERIFY_RECORD_REDACTED": 11,
    "VERIFY_RECORD_ANONYMIZED": 12,
    "VERIFY_DATA_FLOW_DISABLED": 13,
    "VERIFY_RESTORE_BLOCKED": 14,
}
_PHASE_RANK = {"FINDING": 0, "REMEDIATION": 1, "VERIFICATION": 2}


def _scalar_fields(observation: Observation):
    for name, value in observation.fields.items():
        if isinstance(value, (dict, list, tuple, set)) or value is None:
            continue
        yield str(name).split(".")[-1].casefold(), str(value).strip()


def _token_present(text: str, token: str) -> bool:
    if not token:
        return False
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", text, re.IGNORECASE) is not None


def _direct_alias_match(observation: Observation, identity: CaseIdentity) -> bool:
    aliases = identity.aliases
    stable_id = identity.user_id
    for name, raw_value in _scalar_fields(observation):
        if name in _STABLE_ID_FIELDS and raw_value.casefold() == stable_id.casefold():
            return True
        if name in _EXPLICIT_ALIAS_FIELDS:
            kind = FIELD_KIND.get(name, "")
            normalized = normalize_alias(kind, raw_value)
            if normalized in aliases.get(kind, set()):
                return True
        # Some exports use generic selector/lookup fields; exact complete-value
        # equality remains strong evidence and does not use names or edit distance.
        for kind in ("email", "email_hash"):
            if raw_value.casefold() in aliases.get(kind, set()):
                return True

    text = observation.raw_text
    if not text:
        return False
    for alias in aliases.get("email", set()) | aliases.get("email_hash", set()):
        if alias and _token_present(text, alias):
            return True
        # OCR commonly inserts whitespace or punctuation inside table cells.
        # Removing separators still requires every alphanumeric alias character
        # to occur in exact order; no fuzzy edit-distance join is performed.
        compact_text = re.sub(r"[^a-z0-9]", "", text.casefold())
        compact_alias = re.sub(r"[^a-z0-9]", "", alias.casefold())
        if compact_alias and compact_alias in compact_text:
            return True
    if _token_present(text, stable_id):
        return True
    return False


def _valid_for_cutoff(observation: Observation, cutoff: datetime) -> bool:
    return observation.available_at <= cutoff and observation.observed_at <= cutoff


def _event_type(observation: Observation) -> str:
    for name, value in _scalar_fields(observation):
        if name in {"event_type", "event", "operation", "action"}:
            return value.upper()
    return ""


def _field_values(observation: Observation) -> dict[str, list[Any]]:
    values: dict[str, list[Any]] = defaultdict(list)
    for key, value in observation.fields.items():
        values[str(key).split(".")[-1].casefold()].append(value)
    return values


def _source_system_id(observation: Observation) -> str:
    """Prefer explicit logical system fields over a collector/service label.

    Some logs record both the service that collected or queried the evidence
    and the logical system that owns the referenced resource. Resolve named
    source fields by semantic priority rather than their order in the log line.
    """
    values = _field_values(observation)
    for name in ("system_id", "origin_system", "system", "data_store"):
        candidates = {
            str(value).strip()
            for value in values.get(name, [])
            if value is not None and str(value).strip()
        }
        if len(candidates) > 1:
            raise AuditBlocked("source evidence contains conflicting system identifiers")
        if candidates:
            return next(iter(candidates))
    # A logical `source` can be more specific than a replica `service` field.
    # Ignore generic source labels and accept only explicit system-like values.
    manifest_sources = {
        str(value).strip()
        for value in values.get("evidence_origin", [])
        if value is not None and re.fullmatch(
            r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*_(?:service|platform|system|admin|portal)",
            str(value).strip().casefold(),
        )
    }
    if len(manifest_sources) > 1:
        raise AuditBlocked("manifest evidence contains conflicting logical system identifiers")
    if manifest_sources:
        return next(iter(manifest_sources))
    sources = {
        str(value).strip()
        for value in values.get("source", [])
        if value is not None and re.fullmatch(
            r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*_(?:service|platform|system|admin|portal)",
            str(value).strip().casefold(),
        )
    }
    if len(sources) > 1:
        raise AuditBlocked("source evidence contains conflicting logical source identifiers")
    if sources:
        return next(iter(sources))
    for name in ("service", "function", "data_store"):
        candidates = {
            str(value).strip()
            for value in values.get(name, [])
            if value is not None and str(value).strip()
        }
        if len(candidates) > 1:
            raise AuditBlocked("source evidence contains conflicting system identifiers")
        if candidates:
            return next(iter(candidates))
    return observation.system_id


def _explicit_operational_state(observation: Observation, category: str) -> str | None:
    """Interpret explicit process-control fields without confusing row presence with activity."""
    values = _field_values(observation)

    def flags(*names: str) -> set[str]:
        return {
            str(value).strip().casefold()
            for name in names
            for value in values.get(name, [])
            if value is not None
        }

    if category == "DATA_FLOW":
        enabled = flags("enabled", "is_enabled", "flow_enabled", "connector_enabled")
        if enabled and enabled <= {"true", "1", "yes", "enabled", "active"}:
            return "ACTIVE"
        if enabled and enabled <= {"false", "0", "no", "disabled", "inactive"}:
            return "DISABLED"
        status = flags("flow_status", "connector_status", "sync_status")
        if status and status <= {"active", "enabled", "running", "continuous"}:
            return "ACTIVE"
        if status and status <= {"disabled", "inactive", "stopped", "blocked"}:
            return "DISABLED"
        return None

    if category == "BACKUP_ARCHIVE":
        blocked = flags("deletion_block", "restore_blocked", "restore_access_blocked")
        if blocked and blocked <= {"true", "1", "yes", "blocked"}:
            return "BLOCKED"
        eligible = flags("eligible", "restore_eligible", "can_restore", "restore_allowed")
        if eligible and eligible <= {"true", "1", "yes", "eligible", "allowed"}:
            return "ACTIVE"
        return None

    return None


def _parse_policy_date(value: Any):
    text = str(value or "").strip()
    if not text or text.casefold() in {"null", "none", "n/a", "unknown"}:
        return None
    parsed = maybe_instant(text)
    if parsed is not None:
        return parsed.date()
    for pattern in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _explicit_policy_condition(
    observation: Observation,
    category: str,
    cutoff: datetime,
) -> str | None:
    """Resolve policy conditions only from direct, structured evidence fields."""
    values = _field_values(observation)
    if category == "SECURITY_AUDIT_LOG":
        deadlines = {
            _parse_policy_date(value)
            for name in ("retention_until", "retained_until", "retention_end", "retention_expiry", "retained_through")
            for value in values.get(name, [])
        }
        deadlines.discard(None)
        if len(deadlines) == 1:
            return "TRUE" if cutoff.date() <= next(iter(deadlines)) else "FALSE"
        return None

    if category == "BACKUP_ARCHIVE":
        explicit = []
        for name in ("can_block_restore", "restore_blockable", "restore_access_blockable", "can_disable_restore"):
            explicit.extend(values.get(name, []))
        if explicit:
            normalized = {str(value).strip().casefold() for value in explicit if value is not None}
            if normalized and normalized <= {"true", "1", "yes", "available", "supported"}:
                return "TRUE"
            if normalized and normalized <= {"false", "0", "no", "unavailable", "unsupported"}:
                return "FALSE"
            return None
        # A deletion_block field is a direct read of a configurable control;
        # false means the control is not yet applied, not that it is impossible.
        if "deletion_block" in values and any(value is not None for value in values["deletion_block"]):
            return "TRUE"
        if observation.state == "BLOCKED":
            return "TRUE"
        # restore_allowed describes the current state, not the ability to block it.
        return "UNRESOLVED"

    if category == "ACCOUNT_TOMBSTONE":
        status = {
            str(value).strip().casefold()
            for name in ("account_status", "tombstone_status", "deleted")
            for value in values.get(name, [])
            if value is not None and str(value).strip()
        }
        stable_fields = _STABLE_ID_FIELDS | {"subject_ref", "customer_ref"}
        stable_refs = {
            str(value).strip().casefold()
            for name, field_values in values.items()
            if name in stable_fields
            for value in field_values
            if value is not None and str(value).strip().casefold() not in _EMPTY_REFERENCE_VALUES
        }
        deleted_values = {"deleted", "tombstoned", "closed", "true", "1", "yes"}
        not_deleted_values = {"active", "open", "enabled", "false", "0", "no", "not_deleted"}
        if status and status <= deleted_values and stable_refs:
            return "TRUE"
        if status and status <= not_deleted_values:
            return "FALSE"
        if status and status <= deleted_values and not stable_refs:
            if any(
                name in stable_fields and any(value is not None and str(value).strip().casefold() in _EMPTY_REFERENCE_VALUES for value in field_values)
                for name, field_values in values.items()
            ):
                return "FALSE"
        return None
    return None


def _only_stable_identifier_tombstone(observation: Observation, stable_user_id: str) -> bool:
    values = _field_values(observation)
    direct_fields = {"name", "email", "phone", "email_hash"}
    if not direct_fields.issubset(values):
        return False
    for name in direct_fields:
        if any(value is not None and str(value).strip().casefold() not in {"", "null", "none", "n/a"} for value in values[name]):
            return False
    if not any(str(value).strip().casefold() == "deleted" for value in values.get("account_status", [])):
        return False
    stable_fields = _STABLE_ID_FIELDS | {"subject_ref", "customer_ref"}
    return any(
        name in stable_fields and str(value).strip().casefold() == stable_user_id.casefold()
        for name, field_values in values.items()
        for value in field_values
        if value is not None
    )


def _support_policy_input(observation: Observation, observation_id: str, rule: PolicyRule) -> dict[str, Any] | None:
    """Keep a second-pass support policy check limited to direct content/context fields."""
    selected: dict[str, Any] = {}
    for key, value in observation.fields.items():
        normalized = str(key).split(".")[-1].casefold()
        if normalized in _SUPPORT_POLICY_FIELDS and value is not None and str(value).strip():
            selected[normalized] = value
    if not selected and observation.source_kind in {"text", "pdf", "image"} and observation.raw_text.strip():
        selected["source_excerpt"] = observation.raw_text[:1200]
    if not selected or observation.proof_kind not in {"snapshot", "readback"}:
        return None
    return {
        "observation_id": observation_id,
        "category": "SUPPORT_MESSAGE",
        "policy_condition": rule.condition,
        "fields": selected,
        "source_excerpt": observation.raw_text[:1200] if observation.source_kind in {"text", "pdf", "image"} else "",
    }


def _link_identity_matches(
    observation: Observation,
    identity: CaseIdentity,
    resolver: IdentityResolver,
    evidence_cutoff: datetime,
) -> bool:
    return _explicit_subject_link(observation, identity, resolver, evidence_cutoff)


def _has_conflicting_stable_reference(
    observation: Observation,
    identity: CaseIdentity,
    resolver: IdentityResolver,
    evidence_cutoff: datetime,
) -> bool:
    for name, raw_value in _scalar_fields(observation):
        normalized = raw_value.casefold()
        if (
            name not in _STABLE_ID_FIELDS
            or normalized in _EMPTY_REFERENCE_VALUES
            or normalized == identity.user_id.casefold()
        ):
            continue
        alias_match = any(
            normalize_alias(kind, raw_value) in identity.aliases.get(kind, set())
            and resolver.matches_for_evidence(identity.user_id, kind, raw_value, observation.observed_at, evidence_cutoff)
            for kind in ("email", "phone", "email_hash")
        )
        if not alias_match:
            return True
    return False


def _explicit_subject_link(
    observation: Observation,
    identity: CaseIdentity,
    resolver: IdentityResolver,
    evidence_cutoff: datetime,
) -> bool:
    """Promote only a unique exact ID/alias edge valid at observation time."""
    if _has_conflicting_stable_reference(observation, identity, resolver, evidence_cutoff):
        return False
    scalar = list(_scalar_fields(observation))
    if any(name in _STABLE_ID_FIELDS and raw_value.casefold() == identity.user_id.casefold()
           for name, raw_value in scalar):
        return True
    for _, raw_value in scalar:
        for kind in ("email", "phone", "email_hash"):
            if (normalize_alias(kind, raw_value) in identity.aliases.get(kind, set())
                    and resolver.matches_for_evidence(identity.user_id, kind, raw_value, observation.observed_at, evidence_cutoff)):
                return True
    text = observation.raw_text
    if not text:
        return False
    for kind in ("email", "email_hash"):
        for alias in identity.aliases.get(kind, set()):
            if (resolver.matches_for_evidence(identity.user_id, kind, alias, observation.observed_at, evidence_cutoff)
                    and _token_present(text, alias)):
                return True
    compact_text = re.sub(r"[^0-9]", "", text)
    for alias in identity.aliases.get("phone", set()):
        if (len(alias) >= 7 and alias in compact_text
                and resolver.matches_for_evidence(identity.user_id, "phone", alias, observation.observed_at, evidence_cutoff)):
            return True
    return _token_present(text, identity.user_id)


def _linked_resources(
    activity: list[Observation],
    identity: CaseIdentity,
    resolver: IdentityResolver,
    cutoff: datetime,
) -> dict[tuple[str, str], list[str]]:
    linked: dict[tuple[str, str], list[str]] = defaultdict(list)
    link_rows = [
        item for item in activity
        if item.proof_kind == "identity_link"
        and item.system_id and item.resource_id
        and _valid_for_cutoff(item, cutoff)
    ]
    # The source log is not chronologically ordered. Sorting before applying the
    # cutoff prevents appended historical links from being lost or treated as new.
    link_rows.sort(key=lambda item: (item.observed_at, item.evidence_id, item.locator))
    for link in link_rows:
        if _link_identity_matches(link, identity, resolver, cutoff):
            linked[(link.system_id, link.resource_id)].append(link.evidence_id)
    return linked


class CandidateIndex:
    """Exact identifier and resource-link indexes built once per dataset run."""

    def __init__(self, observations: list[Observation], activity: list[Observation]):
        self._stable: dict[str, list[Observation]] = defaultdict(list)
        self._aliases: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        self._by_resource: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        self._text_tokens: dict[str, list[Observation]] = defaultdict(list)
        self._ocr_text: list[tuple[Observation, str]] = []
        self._link_rows = [item for item in activity if item.proof_kind == "identity_link"]
        for item in observations + activity:
            if item.system_id and item.resource_id:
                self._by_resource[(item.system_id, item.resource_id)].append(item)
            indexed_keys: set[tuple[str, str]] = set()
            for name, raw_value in _scalar_fields(item):
                if name in _STABLE_ID_FIELDS:
                    key = raw_value.casefold()
                    if key and key not in indexed_keys:
                        self._stable[key].append(item)
                        indexed_keys.add(key)
                if name in _EXPLICIT_ALIAS_FIELDS:
                    kind = FIELD_KIND.get(name, "")
                    value = normalize_alias(kind, raw_value)
                    key = (kind, value)
                    if kind and value and key not in indexed_keys:
                        self._aliases[key].append(item)
                        indexed_keys.add(key)
                # Preserve the existing exact generic-value match for exports
                # whose schema uses an unrecognized selector column.
                for kind in ("email", "email_hash"):
                    key = (kind, raw_value.casefold())
                    if raw_value and key not in indexed_keys:
                        self._aliases[key].append(item)
                        indexed_keys.add(key)
            if item.raw_text:
                text = item.raw_text.casefold()
                for token in re.findall(r"[a-z0-9_@.+%-]+", text):
                    token = token.strip(".,;:!?()[]{}<>\"'")
                    if token:
                        self._text_tokens[token].append(item)
                if item.source_kind in {"image", "pdf", "text"}:
                    self._ocr_text.append((item, re.sub(r"[^a-z0-9]", "", text)))

    def candidates(
        self,
        identity: CaseIdentity,
        resolver: IdentityResolver,
        cutoff: datetime,
    ) -> tuple[list[Observation], dict[tuple[str, str], list[str]]]:
        linked = _linked_resources(self._link_rows, identity, resolver, cutoff)
        candidates: dict[tuple[str, str], Observation] = {}

        def add(item: Observation) -> None:
            if item.proof_kind == "identity_link" or not _valid_for_cutoff(item, cutoff):
                return
            # Once one observation is exactly linked to the subject, inspect
            # every time-valid observation for that same logical resource.
            # This recovers later scoped readbacks and earlier snapshots that
            # omit the subject identifier, without joining by names or IDs that
            # merely look similar. Conflicting stable references still fail
            # closed during audit validation.
            peers = self._by_resource.get((item.system_id, item.resource_id), []) if item.system_id and item.resource_id else []
            for candidate in [item, *peers]:
                if candidate.proof_kind != "identity_link" and _valid_for_cutoff(candidate, cutoff):
                    candidates[(candidate.evidence_id, candidate.locator)] = candidate

        for item in self._stable.get(identity.user_id.casefold(), []):
            add(item)
        for kind, values in identity.aliases.items():
            for value in values:
                normalized = normalize_alias(kind, value)
                for item in self._aliases.get((kind, normalized), []):
                    if resolver.matches_for_evidence(identity.user_id, kind, normalized, item.observed_at, cutoff):
                        add(item)

        text_aliases = identity.aliases.get("email", set()) | identity.aliases.get("email_hash", set())
        for alias in text_aliases:
            if alias:
                for item in self._text_tokens.get(alias.casefold(), []):
                    kind = "email_hash" if alias.casefold() in identity.aliases.get("email_hash", set()) else "email"
                    if resolver.matches_for_evidence(identity.user_id, kind, alias, item.observed_at, cutoff):
                        add(item)
        for item in self._text_tokens.get(identity.user_id.casefold(), []):
            add(item)

        compact_aliases = {
            re.sub(r"[^a-z0-9]", "", value.casefold())
            for value in text_aliases
            if value
        }
        if compact_aliases:
            for item, compact_text in self._ocr_text:
                if not _valid_for_cutoff(item, cutoff):
                    continue
                if any(
                    re.sub(r"[^a-z0-9]", "", alias.casefold()) in compact_text
                    and resolver.matches_for_evidence(identity.user_id, "email", alias, item.observed_at, cutoff)
                    for alias in text_aliases if alias
                ):
                    add(item)

        for resource_key in linked:
            for item in self._by_resource.get(resource_key, []):
                add(item)
        return sorted(candidates.values(), key=lambda item: (item.evidence_id, item.locator)), linked


def _candidate_observations(
    observations: list[Observation],
    activity: list[Observation],
    identity: CaseIdentity,
    resolver: IdentityResolver,
    cutoff: datetime,
    index: CandidateIndex | None = None,
) -> tuple[list[Observation], dict[tuple[str, str], list[str]]]:
    return (index or CandidateIndex(observations, activity)).candidates(identity, resolver, cutoff)


def _public_candidate(
    observation: Observation,
    index: int,
    linked: dict[tuple[str, str], list[str]],
) -> dict[str, Any]:
    payload = observation_to_public_dict(observation)
    payload["observation_id"] = f"obs-{index:05d}"
    payload["identity_link_evidence_ids"] = linked.get((observation.system_id, observation.resource_id), [])
    return payload


def _validate_classification(
    observation: Observation,
    classification: dict[str, Any],
    stable_user_id: str,
    cutoff: datetime,
) -> ClassifiedFact:
    category = str(classification.get("category", ""))
    if observation.proof_kind in {"readback", "snapshot"} and observation.state != "UNKNOWN":
        # A structured snapshot/readback already proves its normalized state.
        # The model may classify meaning, but may not replace an explicit state.
        if category in {"DATA_FLOW", "BACKUP_ARCHIVE"} and observation.state == "PRESENT":
            operational_state = _explicit_operational_state(observation, category)
            if operational_state is not None:
                classification = {**classification, "state": operational_state}
        else:
            classification = {**classification, "state": observation.state}
    if classification.get("state") == "ABSENT" and observation.proof_kind == "readback":
        # A directly queried, scoped absence means this resource does not
        # currently expose identifiers. Models often mark that field unknown
        # because no row values exist; the readback itself resolves it.
        classification = {**classification, "identifiers_exposed": "NO"}
    if classification.get("relevant_to_subject") not in {"YES", "NO", "UNRESOLVED"}:
        raise AuditBlocked("model returned an invalid relevance value")
    if classification.get("relevant_to_subject") == "UNRESOLVED":
        raise AuditBlocked("model could not resolve a candidate's subject link")
    condition = _explicit_policy_condition(observation, category, cutoff)
    if condition is not None:
        classification = {**classification, "policy_condition": condition}
    if (
        category == "ACCOUNT_TOMBSTONE"
        and classification.get("policy_condition") == "TRUE"
        and _only_stable_identifier_tombstone(observation, stable_user_id)
    ):
        # The supplied tombstone rule permits a stable internal user_id to keep
        # references to retained records; null direct identifiers are not exposure.
        classification = {**classification, "identifiers_exposed": "NO"}
    if category == "UNRESOLVED":
        raise AuditBlocked("model could not classify a material evidence category")
    if classification.get("state") not in {"PRESENT", "ABSENT", "ACTIVE", "DISABLED", "BLOCKED", "REDACTED", "ANONYMIZED", "UNKNOWN"}:
        raise AuditBlocked("model returned an invalid observation state")
    if classification.get("identifiers_exposed") not in {"YES", "NO", "UNRESOLVED"}:
        raise AuditBlocked("model could not resolve identifier exposure")
    if classification.get("policy_condition") not in {"TRUE", "FALSE", "UNRESOLVED", "NOT_APPLICABLE"}:
        raise AuditBlocked("model returned an invalid policy condition")
    if classification.get("scope_complete") not in {"TRUE", "FALSE", "UNRESOLVED", "NOT_APPLICABLE"}:
        raise AuditBlocked("model returned an invalid scope completeness value")

    supplied_system = str(classification.get("system_id", "")).strip()
    supplied_resource = str(classification.get("resource_id", "")).strip()
    source_system = _source_system_id(observation)
    system = source_system or supplied_system
    resource = observation.resource_id or supplied_resource
    scalar_text = "\n".join(value for _, value in _scalar_fields(observation))
    grounded_text = scalar_text + "\n" + observation.raw_text
    system_grounded_text = grounded_text + "\n" + observation.locator
    # Source-extracted identifiers are authoritative. Keep them even when a
    # model response mutates an identifier; only validate model-extracted IDs
    # when the source did not provide a value.
    if source_system:
        system = source_system
        classification["system_id"] = source_system
    elif supplied_system and supplied_system not in system_grounded_text:
        raise AuditBlocked("model extracted a system_id not present in the evidence")
    if observation.resource_id:
        resource = observation.resource_id
        classification["resource_id"] = observation.resource_id
    elif supplied_resource and supplied_resource not in grounded_text:
        raise AuditBlocked("model extracted a resource_id not present in the evidence")
    if not system or not resource:
        raise AuditBlocked("evidence lacks a grounded system_id or resource_id")
    return ClassifiedFact(observation, classification, system, resource)


def reconstruct_current(facts: list[ClassifiedFact]) -> list[CurrentFact]:
    grouped: dict[tuple[str, str, str, str], list[ClassifiedFact]] = defaultdict(list)
    proved_resource_keys: set[tuple[str, str, str]] = set()
    for fact in facts:
        if fact.classification["relevant_to_subject"] == "NO" or fact.observation.proof_kind == "claim":
            continue
        if fact.classification["state"] != "UNKNOWN":
            proved_resource_keys.add((fact.system_id, fact.resource_id, str(fact.classification["category"])))
    for fact in facts:
        if fact.classification["relevant_to_subject"] == "NO":
            continue
        if fact.observation.proof_kind == "claim":
            if (fact.system_id, fact.resource_id, str(fact.classification["category"])) not in proved_resource_keys:
                raise AuditBlocked(f"only workflow claims support {fact.system_id}/{fact.resource_id}")
            continue
        grouped[fact.group_key].append(fact)

    current: list[CurrentFact] = []
    for group, items in grouped.items():
        proved = []
        for fact in items:
            state = str(fact.classification["state"])
            if fact.observation.proof_kind == "claim":
                continue
            if state == "UNKNOWN":
                continue
            if state in {"ABSENT", "DISABLED", "BLOCKED", "REDACTED", "ANONYMIZED"} and fact.observation.proof_kind != "readback":
                continue
            # An explicitly incomplete capture cannot establish global absence,
            # even if a sparse export contains a zero-row marker.
            if state == "ABSENT" and fact.observation.scope_complete is False:
                continue
            if state == "PRESENT" and fact.observation.proof_kind not in {"snapshot", "readback"}:
                continue
            if state == "ACTIVE" and fact.observation.proof_kind not in {"readback", "snapshot"}:
                continue
            proved.append(fact)
        if not proved:
            raise AuditBlocked(f"no scoped state proof for {group[0]}/{group[1]}")
        proved.sort(key=lambda fact: (
            fact.observation.observed_at,
            1 if fact.observation.proof_kind == "readback" else 0,
            fact.observation.available_at,
            fact.observation.evidence_id,
            fact.observation.locator,
        ))
        latest_time = proved[-1].observation.observed_at
        latest = [fact for fact in proved if fact.observation.observed_at == latest_time]
        # At the same event time, a scoped direct readback is stronger than a
        # snapshot row. Conflicting readbacks remain an ambiguity and fail closed.
        readbacks = [fact for fact in latest if fact.observation.proof_kind == "readback"]
        if readbacks:
            latest = readbacks
        state_values = {str(fact.classification["state"]) for fact in latest}
        if group[3] == "DATA_FLOW":
            exposure_values = {"NO"}
            condition_values = {"NOT_APPLICABLE"}
        else:
            exposure_values = {str(fact.classification["identifiers_exposed"]) for fact in latest}
            condition_values = {str(fact.classification["policy_condition"]) for fact in latest}
        if len(state_values) != 1:
            raise AuditBlocked(f"conflicting simultaneous state evidence for {group[0]}/{group[1]}")
        exposure = next(iter(exposure_values)) if len(exposure_values) == 1 else "UNRESOLVED"
        if "UNRESOLVED" in exposure_values:
            exposure = "UNRESOLVED"
        condition = next(iter(condition_values)) if len(condition_values) == 1 else "UNRESOLVED"
        if "UNRESOLVED" in condition_values:
            condition = "UNRESOLVED"
        selected = latest[-1]
        current.append(CurrentFact(
            selected,
            next(iter(state_values)),
            exposure,
            condition,
            selected.observation.evidence_id,
        ))
    return sorted(current, key=lambda item: (item.fact.system_id, item.fact.resource_id, item.fact.group_key[2], item.fact.group_key[3]))


def _record_verification(category: str, treatment: str, state: str) -> tuple[str, str]:
    if state == "ABSENT":
        return "VERIFY_RECORD_ABSENT", "ABSENT"
    if treatment == "DELETE":
        return "VERIFY_RECORD_ABSENT", "ABSENT"
    if category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"}:
        return "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"
    if treatment == "ANONYMIZE":
        return "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"
    if treatment == "REDACT" or category == "EMAIL_DELIVERY_LOG":
        return "VERIFY_RECORD_REDACTED", "REDACTED"
    if treatment == "RETAIN":
        return "VERIFY_RECORD_PRESENT", "PRESENT"
    raise AuditBlocked(f"no verification operation for {category}/{treatment}")


def plan_case(
    case_id: str,
    current: list[CurrentFact],
    rules: dict[str, PolicyRule],
    unresolved: list[str] | None = None,
) -> AuditResult:
    findings: list[dict[str, str]] = []
    remediations: list[dict[str, str]] = []
    verifications: list[dict[str, str]] = []
    needs_action = False

    for item in current:
        fact = item.fact
        category = str(fact.classification["category"])
        state = item.state
        exposed = item.identifiers_exposed
        condition = item.policy_condition

        if category == "DATA_FLOW":
            if state == "ACTIVE":
                needs_action = True
                findings.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "REPORT_ACTIVE_DATA_FLOW", "state": "ACTIVE", "evidence_id": item.evidence_id})
                remediations.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "DISABLE_DATA_FLOW", "state": "DISABLED", "evidence_id": ""})
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_DATA_FLOW_DISABLED", "state": "DISABLED", "evidence_id": ""})
            elif state == "DISABLED":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_DATA_FLOW_DISABLED", "state": "DISABLED", "evidence_id": item.evidence_id})
            elif state == "ABSENT":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": item.evidence_id})
            else:
                raise AuditBlocked(f"data flow {fact.resource_id} has unresolved state {state}")
            continue

        rule = rules.get(category)
        if rule is None:
            raise AuditBlocked(f"no supplied policy rule for {category}")
        try:
            treatment = required_treatment(rule, condition, state)
        except PolicyResolutionError as exc:
            raise AuditBlocked(str(exc)) from None

        if category == "BACKUP_ARCHIVE":
            if state == "ACTIVE":
                needs_action = True
                findings.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "REPORT_RESTORE_RISK", "state": "ACTIVE", "evidence_id": item.evidence_id})
                remediations.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "BLOCK_RESTORE", "state": "BLOCKED", "evidence_id": ""})
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RESTORE_BLOCKED", "state": "BLOCKED", "evidence_id": ""})
                continue
            if state == "BLOCKED":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RESTORE_BLOCKED", "state": "BLOCKED", "evidence_id": item.evidence_id})
                continue
            if state == "ABSENT":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": item.evidence_id})
                continue
            raise AuditBlocked(f"backup {fact.resource_id} has unresolved restore access state")

        if treatment == "COMPLIANT":
            if exposed != "NO":
                raise AuditBlocked(f"{category}/{fact.resource_id}: policy says compliant but identifier exposure is unresolved or present")
            operation, verification_state = _record_verification(category, rule.action, state)
            if state == "PRESENT" and category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"} and condition == "FALSE":
                operation, verification_state = "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"
            verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": operation, "state": verification_state, "evidence_id": item.evidence_id})
            continue

        if treatment == "RETAIN":
            if state != "PRESENT":
                if state == "ABSENT":
                    raise AuditBlocked(f"policy-required retained record {fact.resource_id} is absent")
                raise AuditBlocked(f"policy-required retained record {fact.resource_id} has unresolved state")
            verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_PRESENT", "state": "PRESENT", "evidence_id": item.evidence_id})
            continue

        if treatment == "DELETE":
            if state == "PRESENT":
                needs_action = True
                findings.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "REPORT_REMAINING_RECORD", "state": "PRESENT", "evidence_id": item.evidence_id})
                remediations.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "DELETE_RECORD", "state": "ABSENT", "evidence_id": ""})
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": ""})
            elif state == "ABSENT":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": item.evidence_id})
            else:
                raise AuditBlocked(f"record {fact.resource_id} requiring deletion has unresolved state")
            continue

        if treatment in {"REDACT", "ANONYMIZE"}:
            if state == "ABSENT":
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ABSENT", "state": "ABSENT", "evidence_id": item.evidence_id})
                continue
            if state in {"REDACTED", "ANONYMIZED"} and exposed == "NO":
                operation, verification_state = _record_verification(category, treatment, state)
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": operation, "state": verification_state, "evidence_id": item.evidence_id})
                continue
            if state != "PRESENT":
                raise AuditBlocked(f"record {fact.resource_id} requiring {treatment} has unresolved state")
            if treatment == "REDACT" and exposed == "NO":
                operation, verification_state = _record_verification(category, treatment, state)
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": operation, "state": verification_state, "evidence_id": item.evidence_id})
                continue
            if treatment == "ANONYMIZE" and condition != "TRUE":
                raise AuditBlocked(f"record {fact.resource_id} is not proven attributable for anonymization")
            needs_action = True
            findings.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "REPORT_EXPOSED_PII", "state": "PRESENT", "evidence_id": item.evidence_id})
            if treatment == "REDACT":
                remediations.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "REDACT_RECORD", "state": "REDACTED", "evidence_id": ""})
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_REDACTED", "state": "REDACTED", "evidence_id": ""})
            else:
                remediations.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "ANONYMIZE_RECORD", "state": "ANONYMIZED", "evidence_id": ""})
                verifications.append({"system_id": fact.system_id, "resource_id": fact.resource_id, "operation": "VERIFY_RECORD_ANONYMIZED", "state": "ANONYMIZED", "evidence_id": ""})
            continue

        if treatment == "RETAIN":
            continue
        raise AuditBlocked(f"unsupported resolved policy action {treatment}")

    if needs_action:
        status = "INCOMPLETE"
        # Verification steps in an incomplete plan are future checks, so never
        # claim that they have already passed or attach current evidence IDs.
        for verification in verifications:
            verification["evidence_id"] = ""
    else:
        status = "COMPLETE"
        verifications = [item for item in verifications if item["evidence_id"]]
        if not verifications:
            raise AuditBlocked("no evidence-backed verification supports COMPLETE")

    all_steps = (
        [{"phase": "FINDING", **step} for step in findings]
        + [{"phase": "REMEDIATION", **step} for step in remediations]
        + [{"phase": "VERIFICATION", **step} for step in verifications]
    )
    all_steps.sort(key=lambda step: (
        _PHASE_RANK[step["phase"]],
        _OPERATION_RANK[step["operation"]],
        step["system_id"],
        step["resource_id"],
    ))
    steps = [
        {"step_no": index, **step}
        for index, step in enumerate(all_steps, start=1)
    ]
    return AuditResult(case_id, status, steps, unresolved or [])


def audit_case(
    request: dict[str, str],
    intent: dict[str, str],
    resolver: IdentityResolver,
    observations: list[Observation],
    activity: list[Observation],
    rules: dict[str, PolicyRule],
    model: Any,
    evidence_prompt: str,
    candidate_index: CandidateIndex | None = None,
    policy_condition_prompt: str | None = None,
) -> AuditResult:
    case_id = request["case_id"]
    decision = intent.get("intent", "UNRESOLVED")
    confidence = intent.get("confidence", "LOW")
    if decision == "UNRESOLVED" or confidence == "LOW":
        raise AuditBlocked(f"{case_id}: deletion intent is unresolved")
    if decision == "NOT_DELETE":
        return AuditResult(case_id, "NOT_APPLICABLE", [])
    if decision != "DELETE":
        raise AuditBlocked(f"{case_id}: invalid deletion intent")

    requested_at = parse_instant(request["requested_at"])
    cutoff = parse_instant(request["audit_at"])
    identity = resolver.resolve(request["email"], requested_at, cutoff)
    if identity is None:
        raise AuditBlocked(f"{case_id}: stable subject could not be resolved unambiguously")

    candidates, linked = _candidate_observations(observations, activity, identity, resolver, cutoff, candidate_index)
    if not candidates:
        raise AuditBlocked(f"{case_id}: no subject-linked evidence supports an audit decision")
    public = [_public_candidate(item, index, linked) for index, item in enumerate(candidates, start=1)]
    classified = classify_observations(
        model,
        case_id,
        identity.user_id,
        cutoff.isoformat(),
        public,
        evidence_prompt,
        model_policy_payload(rules),
        {
            "stable_user_id": identity.user_id,
            "time_valid_aliases_as_of_audit": {
                kind: sorted(values)
                for kind, values in identity.aliases.items()
                if kind in {"email", "phone", "email_hash"}
            },
            "identity_evidence_ids": identity.evidence_ids,
        },
    )

    if policy_condition_prompt:
        condition_inputs: list[dict[str, Any]] = []
        condition_ids: list[str] = []
        for index, observation in enumerate(candidates, start=1):
            observation_id = f"obs-{index:05d}"
            item = classified[observation_id]
            category = str(item.get("category", ""))
            if category != "SUPPORT_MESSAGE" or item.get("policy_condition") != "UNRESOLVED":
                continue
            rule = rules.get(category)
            if rule is None:
                continue
            policy_input = _support_policy_input(observation, observation_id, rule)
            if policy_input is not None:
                condition_inputs.append(policy_input)
                condition_ids.append(observation_id)
        if condition_inputs:
            try:
                resolved_conditions = classify_policy_conditions(
                    model, case_id, cutoff.isoformat(), condition_inputs, policy_condition_prompt,
                )
            except (ModelCallError, ValueError) as exc:
                raise AuditBlocked(f"{case_id}: support policy recheck failed ({type(exc).__name__})") from None
            for observation_id in condition_ids:
                classified[observation_id]["policy_condition"] = resolved_conditions[observation_id]["condition"]
                classified[observation_id]["policy_condition_recheck_reason"] = resolved_conditions[observation_id]["reason"]

    facts: list[ClassifiedFact] = []
    for index, observation in enumerate(candidates, start=1):
        classification = dict(classified[f"obs-{index:05d}"])
        if _has_conflicting_stable_reference(observation, identity, resolver, cutoff):
            raise AuditBlocked(f"{case_id}: evidence contains a conflicting stable subject reference")
        if public[index - 1]["identity_link_evidence_ids"] or _explicit_subject_link(observation, identity, resolver, cutoff):
            classification["relevant_to_subject"] = "YES"
        if classification.get("relevant_to_subject") == "NO":
            continue
        facts.append(_validate_classification(observation, classification, identity.user_id, cutoff))
    if not facts:
        raise AuditBlocked(f"{case_id}: no candidate record was confirmed relevant")
    current = reconstruct_current(facts)
    return plan_case(case_id, current, rules)
