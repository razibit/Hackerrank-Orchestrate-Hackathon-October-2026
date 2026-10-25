from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class EvidenceSource:
    evidence_id: str
    path: str
    origin: str
    captured_at: datetime


@dataclass
class Observation:
    """One provenance-preserving observation extracted from a single source."""

    evidence_id: str
    locator: str
    available_at: datetime
    observed_at: datetime
    system_id: str
    resource_id: str
    scope_id: str
    category: str
    state: str
    fields: dict[str, Any] = field(default_factory=dict)
    source_kind: str = "file"
    proof_kind: str = "snapshot"
    scope_complete: bool | None = None
    raw_text: str = ""
    trace_id: str = ""

    @property
    def key(self) -> tuple[str, str, str, str]:
        return (self.system_id, self.resource_id, self.scope_id, self.category)


@dataclass(frozen=True)
class IdentityAlias:
    user_id: str
    field_name: str
    value: str
    valid_from: datetime | None
    valid_to: datetime | None
    evidence_time: datetime | None
    evidence_id: str
    source_kind: str


@dataclass
class CaseIdentity:
    user_id: str
    aliases: dict[str, set[str]]
    evidence_ids: list[str]
    matched_aliases: list[str]


@dataclass
class AuditResult:
    case_id: str
    deletion_status: str
    steps: list[dict[str, Any]]
    unresolved: list[str] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)


def observation_to_public_dict(observation: Observation) -> dict[str, Any]:
    """Return bounded, non-secret context for semantic model classification."""
    payload: dict[str, Any] = {}
    for key, value in observation.fields.items():
        normalized = str(key).split(".")[-1].casefold()
        if any(secret in normalized for secret in ("password", "secret", "credential", "access_token", "private_key")):
            continue
        if not isinstance(value, (dict, list, tuple, set)) and value is not None:
            rendered = str(value)
            if len(rendered) <= 1500 and len(payload) < 100:
                payload[key] = value
    raw = observation.raw_text.strip()
    return {
        "evidence_id": observation.evidence_id,
        "locator": observation.locator,
        "observed_at": observation.observed_at.isoformat(),
        "system_id": observation.system_id,
        "resource_id": observation.resource_id,
        "scope_id": observation.scope_id,
        "category_hint": observation.category,
        "state_hint": observation.state,
        "proof_kind": observation.proof_kind,
        "scope_complete": observation.scope_complete,
        "fields": payload,
        "excerpt": raw[:1200],
    }
