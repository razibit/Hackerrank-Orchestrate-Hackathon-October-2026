from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime, timezone
from typing import Any


_SECURITY_RETENTION_FIELD = "retention_until"
_LEGAL_HOLD_STATUS_FIELDS = {
    "hold_status", "hold_state", "legal_hold_status", "legal_hold_state",
}
_LEGAL_HOLD_ACTIVE_FIELDS = {
    "hold_active", "is_hold_active", "legal_hold_active", "is_legal_hold_active",
}
_LEGAL_HOLD_TRUE = {"active", "in_effect", "in_force", "true", "1", "yes"}
_LEGAL_HOLD_FALSE = {
    "cancelled", "canceled", "closed", "expired", "inactive", "lifted",
    "not_active", "released", "terminated", "false", "0", "no",
}
_ACTIVE_VALUES = {"active", "open", "enabled", "true", "1", "yes"}
_INACTIVE_VALUES = {"false", "0", "no", "not_deleted"}
_DELETED_VALUES = {"deleted", "tombstoned", "true", "1", "yes"}
_EMPTY_REFERENCE_VALUES = {"", "null", "none", "n/a", "na"}
_STABLE_REFERENCE_FIELDS = {
    "user_id", "subject_id", "subject_reference", "customer_reference",
    "subject_ref", "subject_key", "user_ref", "owner_ref", "customer_ref",
    "customer_id", "owner_user_id", "principal_id", "identity_id",
}
_SUPPORT_CONTENT_FIELDS = {
    "message", "message_body", "message_excerpt", "message_text", "content_text",
    "conversation_text", "thread_text", "body_text", "shared_context",
}
_SUPPORT_CONTENT_SOURCE_KINDS = {"text", "pdf", "image"}
_SUPPORT_NONCONTENT_VALUES = _EMPTY_REFERENCE_VALUES | {"unknown", "unresolved"}
_ACTIVE_HOLD_TEXT = re.compile(
    r"\b(?:(?:active|current|in[- ]effect|in[- ]force)\s+(?:legal|litigation)\s+hold|"
    r"(?:legal|litigation)\s+hold\s+(?:is\s+|remains\s+)?(?:currently\s+)?"
    r"(?:active|current|in[- ]effect|in[- ]force))\b",
    re.IGNORECASE,
)
_INACTIVE_HOLD_TEXT = re.compile(
    r"\b(?:no\s+(?:active\s+)?(?:legal|litigation)\s+hold|"
    r"not\s+(?:an?\s+)?(?:active\s+)?(?:legal|litigation)\s+hold|"
    r"(?:legal|litigation)\s+hold\s+(?:is\s+|remains\s+)?"
    r"(?:not\s+active|inactive|released|lifted|expired|closed|cancelled|canceled|not\s+in\s+effect))\b",
    re.IGNORECASE,
)
_UNCERTAIN_HOLD_TEXT = re.compile(
    r"\bno\s+(?:evidence|indication|record|confirmation)\s+(?:of|that)\b.{0,100}"
    r"\b(?:legal|litigation)\s+hold\b|"
    r"\b(?:unclear|uncertain|unknown|undetermined|not\s+clear|cannot\s+determine|"
    r"unable\s+to\s+determine)\b.{0,100}\b(?:legal|litigation)\s+hold\b|"
    r"\b(?:legal|litigation)\s+hold\b.{0,80}\b(?:unclear|uncertain|unknown|undetermined)\b",
    re.IGNORECASE,
)
_BACKUP_CAN_BLOCK_TEXT = re.compile(
    r"\bcan\s+(?:block|disable|prevent)\s+(?:future\s+)?restor(?:e|es|ation)\b|"
    r"\brestor(?:e|es|ation)(?:\s+access)?\s+can\s+be\s+blocked\b|"
    r"\brestore[- ]block(?:ing)?\s+(?:is\s+)?(?:available|supported|possible|enabled)\b",
    re.IGNORECASE,
)
_BACKUP_CANNOT_BLOCK_TEXT = re.compile(
    r"\b(?:cannot|can't|unable\s+to)\s+(?:block|disable|prevent)\s+(?:future\s+)?restor(?:e|es|ation)\b|"
    r"\brestor(?:e|es|ation)(?:\s+access)?\s+cannot\s+be\s+blocked\b|"
    r"\brestore[- ]block(?:ing)?\s+(?:is\s+)?(?:unavailable|unsupported|impossible)\b",
    re.IGNORECASE,
)
_UNCERTAIN_BACKUP_TEXT = re.compile(
    r"\b(?:unclear|uncertain|unknown|undetermined|not\s+sure|not\s+known|unconfirmed|"
    r"cannot\s+confirm|unable\s+to\s+confirm|cannot\s+determine|unable\s+to\s+determine)\b"
    r".{0,100}\b(?:restore|restoration|block|blocked|blocking)\b|"
    r"\b(?:restore|restoration)\b.{0,100}\b(?:unclear|uncertain|unknown|undetermined|"
    r"not\s+sure|not\s+known|unconfirmed)\b",
    re.IGNORECASE,
)


def _field_values(fields: Mapping[str, Any]) -> dict[str, list[Any]]:
    values: dict[str, list[Any]] = defaultdict(list)
    for raw_name, value in fields.items():
        values[str(raw_name).split(".")[-1].casefold()].append(value)
    return values


def _normalized(value: Any) -> str:
    return str(value).strip().casefold().replace("-", "_").replace(" ", "_")


def _date_value(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text or text.casefold() in _EMPTY_REFERENCE_VALUES | {"unknown"}:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).date()
    except ValueError:
        pass
    for pattern in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def support_message_has_content(
    fields: Mapping[str, Any], *, raw_text: str = "", source_kind: str = "",
) -> bool:
    """Return whether a support policy decision has actual message/context content."""
    for name, values in _field_values(fields).items():
        if name not in _SUPPORT_CONTENT_FIELDS:
            continue
        if any(
            isinstance(value, str)
            and value.strip()
            and _normalized(value) not in _SUPPORT_NONCONTENT_VALUES
            for value in values
        ):
            return True
    return source_kind.casefold() in _SUPPORT_CONTENT_SOURCE_KINDS and bool(raw_text.strip())


def resolve_policy_condition_from_fields(
    category: str,
    fields: Mapping[str, Any],
    observed_state: str,
    audit_at: datetime,
    *,
    stable_user_id: str | None = None,
    raw_text: str = "",
    source_kind: str = "",
    proof_kind: str = "snapshot",
) -> str | None:
    """Resolve conditions that have a deterministic, structured evidence test.

    A returned ``UNRESOLVED`` is authoritative and should override a semantic
    classifier's guess. ``None`` means that this helper has no deterministic
    decision for the category, so the caller may use its validated classifier.
    """
    values = _field_values(fields)

    if category == "SECURITY_AUDIT_LOG":
        # The supplied security-log schema uses retention_until. Generic legal
        # dates such as retained_until do not establish security-log retention.
        raw_deadlines = [
            value for value in values.get(_SECURITY_RETENTION_FIELD, [])
            if value is not None and str(value).strip()
        ]
        deadlines = {_date_value(value) for value in raw_deadlines}
        if not raw_deadlines or None in deadlines or len(deadlines) != 1:
            return "UNRESOLVED"
        return "TRUE" if audit_at.date() <= next(iter(deadlines)) else "FALSE"

    if category == "LEGAL_HOLD_RECORD":
        signals: set[str] = set()
        for name, field_values in values.items():
            if name not in _LEGAL_HOLD_STATUS_FIELDS | _LEGAL_HOLD_ACTIVE_FIELDS:
                continue
            for value in field_values:
                if value is None or not str(value).strip():
                    continue
                normalized = _normalized(value)
                if name in _LEGAL_HOLD_ACTIVE_FIELDS:
                    if normalized in {"true", "1", "yes", "active", "enabled"}:
                        signals.add("TRUE")
                    elif normalized in {"false", "0", "no", "inactive", "disabled"}:
                        signals.add("FALSE")
                    else:
                        return "UNRESOLVED"
                elif normalized in _LEGAL_HOLD_TRUE:
                    signals.add("TRUE")
                elif normalized in _LEGAL_HOLD_FALSE:
                    signals.add("FALSE")
                else:
                    return "UNRESOLVED"
        for sentence in re.split(r"(?<=[.!?;\n])\s*", raw_text):
            if _UNCERTAIN_HOLD_TEXT.search(sentence):
                return "UNRESOLVED"
            if _INACTIVE_HOLD_TEXT.search(sentence):
                signals.add("FALSE")
            elif _ACTIVE_HOLD_TEXT.search(sentence):
                signals.add("TRUE")
        return next(iter(signals)) if len(signals) == 1 else "UNRESOLVED"

    if category == "SUPPORT_MESSAGE":
        if not support_message_has_content(
            fields, raw_text=raw_text, source_kind=source_kind,
        ):
            return "UNRESOLVED"
        # Relevant shared context is semantic; it must be evaluated from the
        # supplied message text by the validated policy-condition classifier.
        return None

    if category == "BACKUP_ARCHIVE":
        if proof_kind not in {"snapshot", "readback"}:
            return "UNRESOLVED"
        capability_fields = (
            "can_block_restore", "restore_blockable", "restore_access_blockable",
            "can_disable_restore",
        )
        capability_values = [
            value for name in capability_fields for value in values.get(name, [])
            if value is not None and str(value).strip()
        ]
        if capability_values:
            answers = set()
            for value in capability_values:
                normalized = _normalized(value)
                if normalized in {"true", "1", "yes", "available", "supported"}:
                    answers.add("TRUE")
                elif normalized in {"false", "0", "no", "unavailable", "unsupported"}:
                    answers.add("FALSE")
                else:
                    return "UNRESOLVED"
            return next(iter(answers)) if len(answers) == 1 else "UNRESOLVED"
        # A false control value means it is not applied; it does not prove the
        # system can apply it. Only an explicit true value proves a blocked control.
        block_values = [
            _normalized(value) for value in values.get("deletion_block", [])
            if value is not None and str(value).strip()
        ]
        if block_values:
            if set(block_values) <= {"true", "1", "yes", "blocked"}:
                return "TRUE"
            if set(block_values) <= {"false", "0", "no", "not_applied"}:
                return "UNRESOLVED"
            return "UNRESOLVED"
        if observed_state.upper() == "BLOCKED":
            return "TRUE"
        if observed_state.upper() == "ABSENT":
            return "FALSE"
        if source_kind.casefold() in _SUPPORT_CONTENT_SOURCE_KINDS and raw_text.strip():
            positive = bool(_BACKUP_CAN_BLOCK_TEXT.search(raw_text))
            negative = bool(_BACKUP_CANNOT_BLOCK_TEXT.search(raw_text))
            uncertain = bool(_UNCERTAIN_BACKUP_TEXT.search(raw_text))
            if uncertain or positive == negative:
                return "UNRESOLVED"
            return "TRUE" if positive else "FALSE"
        # Restore eligibility/permission is current state, not blocking ability.
        return "UNRESOLVED"

    if category == "ACCOUNT_TOMBSTONE":
        raw_statuses = [
            _normalized(value)
            for name in ("account_status", "tombstone_status", "deleted")
            for value in values.get(name, [])
            if value is not None and str(value).strip()
        ]
        status_answers = {
            "TRUE" if value in _DELETED_VALUES else
            "FALSE" if value in _ACTIVE_VALUES | _INACTIVE_VALUES | {"inactive"} else
            "UNRESOLVED"
            for value in raw_statuses
        }
        if not raw_statuses or len(status_answers) != 1 or "UNRESOLVED" in status_answers:
            return "UNRESOLVED"
        status_answer = next(iter(status_answers))
        if status_answer == "FALSE":
            return "FALSE"
        stable_values = {
            _normalized(value)
            for name, field_values in values.items()
            if name in _STABLE_REFERENCE_FIELDS
            for value in field_values
            if value is not None and _normalized(value) not in _EMPTY_REFERENCE_VALUES
        }
        if stable_values and stable_user_id is not None:
            expected = stable_user_id.strip().casefold()
            return "TRUE" if expected and stable_values == {expected} else "UNRESOLVED"
        if stable_values:
            return "TRUE"
        if any(
            name in _STABLE_REFERENCE_FIELDS
            and any(value is not None and _normalized(value) in _EMPTY_REFERENCE_VALUES for value in field_values)
            for name, field_values in values.items()
        ):
            return "FALSE"
        return "UNRESOLVED"

    return None


def tombstone_has_only_stable_reference(
    fields: Mapping[str, Any], stable_user_id: str,
) -> bool:
    """Check the supplied tombstone shape against the subject's stable ID."""
    values = _field_values(fields)
    required_null_fields = {"name", "email", "phone", "email_hash"}
    direct_identifier_fields = required_null_fields | {
        "email_address", "email_sha256", "full_name", "hashed_email",
        "mobile", "phone_number",
    }
    if not required_null_fields.issubset(values):
        return False
    for name in direct_identifier_fields:
        if any(
            value is not None and _normalized(value) not in _EMPTY_REFERENCE_VALUES
            for value in values.get(name, [])
        ):
            return False

    statuses = {
        _normalized(value)
        for name in ("account_status", "tombstone_status", "deleted")
        for value in values.get(name, [])
        if value is not None and str(value).strip()
    }
    if not statuses or not statuses <= _DELETED_VALUES:
        return False

    expected = stable_user_id.strip().casefold()
    stable_values = {
        _normalized(value)
        for name, field_values in values.items()
        if name in _STABLE_REFERENCE_FIELDS
        for value in field_values
        if value is not None and _normalized(value) not in _EMPTY_REFERENCE_VALUES
    }
    return bool(expected) and stable_values == {expected}
