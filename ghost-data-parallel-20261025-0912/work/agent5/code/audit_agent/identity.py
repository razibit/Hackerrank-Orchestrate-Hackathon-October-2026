from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from .data import maybe_instant
from .types import CaseIdentity, IdentityAlias


FIELD_KIND = {
    "email": "email",
    "email_address": "email",
    "phone": "phone",
    "phone_number": "phone",
    "mobile": "phone",
    "email_hash": "email_hash",
    "email_sha256": "email_hash",
    "hashed_email": "email_hash",
}


def normalize_alias(field_name: str, value: str) -> str:
    value = str(value or "").strip()
    kind = FIELD_KIND.get(field_name.lower(), field_name.lower())
    if kind in {"email", "email_hash"}:
        return value.casefold()
    if kind == "phone":
        digits = "".join(char for char in value if char.isdigit())
        return digits if len(digits) >= 7 else value.casefold()
    return value.casefold()


class IdentityResolver:
    """Resolve stable user IDs through time-scoped aliases, never display names."""

    def __init__(self, identities: list[dict[str, str]], audit_rows: list[dict[str, str]]):
        self._aliases: list[IdentityAlias] = []
        self._by_user: dict[str, list[IdentityAlias]] = defaultdict(list)
        self._audit_times: dict[str, datetime] = {}
        self._build(identities, audit_rows)

    def _add(self, alias: IdentityAlias) -> None:
        if not alias.value:
            return
        self._aliases.append(alias)
        self._by_user[alias.user_id].append(alias)

    def _build(self, identities: list[dict[str, str]], audit_rows: list[dict[str, str]]) -> None:
        grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in audit_rows:
            user_id = row.get("user_id", "").strip()
            field_name = FIELD_KIND.get(row.get("field_name", "").strip().lower())
            event_time = maybe_instant(row.get("event_time"))
            if not user_id or not field_name or event_time is None:
                continue
            grouped[(user_id, field_name)].append(row)

        for (user_id, field_name), events in grouped.items():
            events.sort(key=lambda row: maybe_instant(row.get("event_time")) or datetime.min.replace(tzinfo=timezone.utc))
            times = [maybe_instant(row.get("event_time")) for row in events]
            for index, row in enumerate(events):
                event_time = times[index]
                assert event_time is not None
                next_time = times[index + 1] if index + 1 < len(times) else None
                old_value = row.get("old_value", "").strip()
                new_value = row.get("new_value", "").strip()
                if old_value:
                    self._add(IdentityAlias(
                        user_id, field_name, normalize_alias(field_name, old_value), None,
                        event_time, event_time, row.get("audit_id", ""), "audit",
                    ))
                if new_value:
                    self._add(IdentityAlias(
                        user_id, field_name, normalize_alias(field_name, new_value), event_time,
                        next_time, event_time, row.get("audit_id", ""), "audit",
                    ))

        for row in identities:
            user_id = row.get("user_id", "").strip()
            valid_from = maybe_instant(row.get("updated_at"))
            if not user_id:
                continue
            for column, kind in (("email", "email"), ("phone", "phone"), ("email_hash", "email_hash")):
                value = row.get(column, "").strip()
                if value:
                    self._add(IdentityAlias(user_id, kind, normalize_alias(kind, value), valid_from, None, valid_from, "", "snapshot"))

    @staticmethod
    def _valid_on(alias: IdentityAlias, instant: datetime) -> bool:
        return (alias.valid_from is None or alias.valid_from <= instant) and (
            alias.valid_to is None or instant < alias.valid_to
        )

    def resolve(self, request_email: str, requested_at: datetime, audit_at: datetime) -> CaseIdentity | None:
        value = normalize_alias("email", request_email)
        candidates = [a for a in self._aliases if a.field_name == "email" and a.value == value
                      and (a.evidence_time is None or a.evidence_time <= audit_at)
                      and (a.valid_from is None or a.valid_from <= audit_at)]
        if not candidates:
            return None

        active_at_request = {a.user_id for a in candidates if self._valid_on(a, requested_at)}
        historical_at_request = {a.user_id for a in candidates if a.valid_from is None or a.valid_from <= requested_at}
        subject_ids = active_at_request if active_at_request else historical_at_request
        if len(subject_ids) != 1:
            return None
        user_id = next(iter(subject_ids))

        aliases: dict[str, set[str]] = {"email": set(), "phone": set(), "email_hash": set(), "user_id": {user_id}}
        evidence_ids: set[str] = set()
        matched_aliases: set[str] = {value}
        for alias in self._by_user.get(user_id, []):
            if alias.valid_from is not None and alias.valid_from > audit_at:
                continue
            if alias.evidence_time is not None and alias.evidence_time > audit_at:
                continue
            aliases.setdefault(alias.field_name, set()).add(alias.value)
            if alias.evidence_id and alias.field_name == "email" and alias.value == value:
                evidence_ids.add(alias.evidence_id)
                matched_aliases.add(alias.value)
            elif alias.evidence_id and alias.valid_from is not None and alias.valid_from <= audit_at:
                evidence_ids.add(alias.evidence_id)

        if value not in aliases["email"]:
            aliases["email"].add(value)
        return CaseIdentity(user_id, aliases, sorted(evidence_ids), sorted(matched_aliases))

    def matches_as_of(
        self,
        user_id: str,
        field_name: str,
        value: str,
        instant: datetime,
        evidence_cutoff: datetime | None = None,
    ) -> bool:
        """Check an identifier at an event time using evidence known by cutoff."""
        kind = FIELD_KIND.get(field_name.casefold(), field_name.casefold())
        normalized = normalize_alias(kind, value)
        evidence_cutoff = evidence_cutoff or instant
        owners = {
            alias.user_id for alias in self._aliases
            if alias.field_name == kind
            and alias.value == normalized
            and self._valid_on(alias, instant)
            and (alias.evidence_time is None or alias.evidence_time <= evidence_cutoff)
        }
        return owners == {user_id}

    def matches_for_evidence(
        self,
        user_id: str,
        field_name: str,
        value: str,
        observed_at: datetime,
        evidence_cutoff: datetime,
    ) -> bool:
        """Match an identifier in an observation without reviving a reassigned alias.

        A record can continue to expose an identifier after that identifier was
        removed from the subject's live account. Such a residual record is still
        attributable when the identity history uniquely links the alias to this
        subject and no other owner is active at the record observation time.
        If another owner is active, or historical ownership is ambiguous, the
        exact string alone is insufficient and the join is rejected.
        """
        kind = FIELD_KIND.get(field_name.casefold(), field_name.casefold())
        normalized = normalize_alias(kind, value)
        known = [
            alias for alias in self._aliases
            if alias.field_name == kind
            and alias.value == normalized
            and (alias.evidence_time is None or alias.evidence_time <= evidence_cutoff)
        ]
        active_owners = {
            alias.user_id for alias in known
            if self._valid_on(alias, observed_at)
        }
        if active_owners:
            return active_owners == {user_id}

        historical_owners = {
            alias.user_id for alias in known
            if (alias.valid_from is None or alias.valid_from <= observed_at)
            and alias.valid_to is not None
            and alias.valid_to <= observed_at
        }
        return historical_owners == {user_id}
