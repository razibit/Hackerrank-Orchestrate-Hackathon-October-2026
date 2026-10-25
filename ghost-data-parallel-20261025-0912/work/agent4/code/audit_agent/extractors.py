from __future__ import annotations

import json
import re
import shlex
import shutil
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .data import maybe_instant, parse_instant, path_is_within, read_csv
from .types import EvidenceSource, Observation


ID_KEYS = {
    "resource_id", "record_id", "object_id", "account_id", "ticket_id",
    "export_id", "archive_id", "data_flow_id", "attachment_id", "document_id",
}
TIME_KEYS = ("observed_at", "event_time", "event_at", "recorded_at", "timestamp", "snapshot_captured_at", "captured_at")


def _flat_fields(value: Any, parent: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            key = str(key)
            path = f"{parent}.{key}" if parent else key
            if isinstance(child, dict):
                result.update(_flat_fields(child, path))
            elif isinstance(child, list):
                if all(not isinstance(item, (dict, list)) for item in child):
                    result[path] = child
                    result.setdefault(key, child)
                else:
                    for index, item in enumerate(child):
                        result.update(_flat_fields(item, f"{path}[{index}]"))
            else:
                result[path] = child
                result.setdefault(key, child)
    else:
        result[parent or "value"] = value
    return result


def _lookup(fields: dict[str, Any], *names: str) -> str:
    wanted = {name.lower() for name in names}
    for key, value in fields.items():
        if str(key).split(".")[-1].lower() in wanted and value is not None and str(value).strip():
            if isinstance(value, (dict, list)):
                continue
            return str(value).strip()
    return ""


def _resource_id(fields: dict[str, Any]) -> str:
    return _lookup(fields, *ID_KEYS)


def _system_id(fields: dict[str, Any], table: str = "") -> str:
    explicit = _lookup(fields, "system_id", "origin_system", "system", "data_store")
    # Some collectors preserve the logical owner in `source` while `service`
    # names the replica or process that queried it. Only accept source values
    # that look like a named system; collector labels such as
    # `records_assurance_gateway` remain provenance, not the owning system.
    manifest_system = _source_system_hint(_lookup(fields, "evidence_origin"))
    logical_source = _source_system_hint(_lookup(fields, "source"))
    if not explicit:
        explicit = manifest_system or logical_source or _lookup(fields, "service", "function")
    event = _lookup(fields, "event_type", "event", "operation", "action").upper()
    role = ("source_system", "target_system") if event in {
        "CHECK_DATA_FLOW", "DISABLE_DATA_FLOW", "CHECK_RESTORE_ACCESS", "BLOCK_RESTORE", "RESTORE_BACKUP"
    } else ("target_system", "source_system")
    value = explicit or _lookup(fields, *role)
    if not value and table:
        table_map = {
            "customer_profiles": "account_service",
            "customer_data_primary": "customer_data_primary",
            "customer_data_read_replica": "customer_data_read_replica",
            "customer_data_replica_ap_south": "customer_data_replica_ap_south",
            "customer_data_replica_eu_west": "customer_data_replica_eu_west",
            "customer_data_reporting_replica": "customer_data_reporting_replica",
            "customer_data_failover_replica": "customer_data_failover_replica",
            # Keep the logical service stable and preserve the failover copy in
            # scope_id; output consumers expect system and physical scope as
            # separate concepts.
            "customer_profiles_failover_replica": "account_service",
            "customer_search_documents": "search_service",
            "search_documents_primary": "search_service",
            "customer_analytics_profiles": "analytics_service",
            "support_records": "support_platform",
            "customer_exports": "export_service",
            "connector_subscriptions": "integration_service",
            "backup_restore_entries": "backup_service",
            "security_audit_records": "security_service",
        }
        value = table_map.get(table, "")
    value = value.strip().replace("-", "_").replace(" ", "_")
    return value


def infer_category(fields: dict[str, Any], table: str = "", source_kind: str = "") -> str:
    """Infer only from record/schema semantics; never inspect resource_id prefixes."""
    explicit = _lookup(fields, "data_category", "category", "record_type", "collection", "collection_name", "table", "data_type")
    schema = " ".join((table, explicit, _lookup(fields, "event_type", "event", "kind", "entity_type"))).casefold()
    rules = (
        ("ACCOUNT_TOMBSTONE", ("account_tombstone", "deleted_account_reference", "deleted_customer_reference", "tombstone")),
        ("SUPPORT_ATTACHMENT", ("support_attachment", "attachment", "uploaded_document")),
        ("SUPPORT_MESSAGE", ("support_message", "support_ticket", "support_record", "conversation", "message")),
        ("ANALYTICS_PROFILE", ("analytics_profile", "customer_analytics_profiles")),
        ("PRODUCT_TELEMETRY", ("product_telemetry", "telemetry_event", "product_event")),
        ("EMAIL_DELIVERY_LOG", ("email_delivery_log", "delivery_log", "email_delivery")),
        ("SECURITY_AUDIT_LOG", ("security_audit", "audit_record", "audit_ledger", "security_journal")),
        ("LEGAL_HOLD_RECORD", ("legal_hold", "retention_register", "legal_retention")),
        ("BACKUP_ARCHIVE", ("backup_archive", "backup_restore", "archive_entry", "restore_entry")),
        ("USER_EXPORT", ("user_export", "customer_export", "export_job", "export_manifest")),
        ("MARKETING_PROFILE", ("marketing_profile", "marketing_contact")),
        ("SEARCH_INDEX_ENTRY", ("search_index", "search_document", "index_document", "search_documents")),
        ("CACHE_ENTRY", ("cache_entry", "profile_cache", "cache_record")),
        ("SECONDARY_IDENTIFIER", ("secondary_identifier", "identifier_record")),
        ("USER_PROFILE", ("user_profile", "customer_profile", "customer_profiles", "account_profile")),
    )
    for category, needles in rules:
        if any(needle in schema for needle in needles):
            return category
    return ""


def _scope_complete(fields: dict[str, Any]) -> bool | None:
    for name in ("scope_complete", "complete_snapshot", "export_complete", "is_complete", "complete"):
        value = _lookup(fields, name).casefold()
        if value in {"true", "1", "yes", "complete", "completed", "succeeded"}:
            return True
        if value in {"false", "0", "no", "partial", "incomplete", "failed"}:
            return False
    dropped = _lookup(fields, "dropped", "dropped_events", "dropped_records")
    if dropped:
        try:
            return int(dropped) == 0
        except ValueError:
            return None
    return None


def _source_system_hint(origin: str) -> str:
    """Use an explicit system-like manifest origin as provenance when a row omits it."""
    value = str(origin or "").strip().casefold().replace("-", "_").replace(" ", "_")
    if re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*_(?:service|platform|system|admin|portal)", value):
        return value
    return ""


def _observation_state(fields: dict[str, Any], category: str, default: str = "PRESENT") -> tuple[str, str]:
    event = _lookup(fields, "event_type", "event", "operation", "action").casefold()
    explicit = _lookup(fields, "observed_state", "record_state", "state", "presence", "lookup_result").casefold()
    rows = _lookup(fields, "rows", "row_count", "result_count", "hits")
    code = _lookup(fields, "http_status", "status_code", "http_code")
    if explicit in {"absent", "not_found", "not found", "missing", "deleted", "404", "410"}:
        return "ABSENT", "readback" if any(token in event for token in ("lookup", "read", "query", "check")) else "claim"
    if rows:
        try:
            if int(rows) == 0:
                return "ABSENT", "readback"
            if int(rows) > 0:
                return "PRESENT", "readback"
        except ValueError:
            pass
    if code in {"404", "410"}:
        return "ABSENT", "readback"
    if code and code.startswith("2"):
        if any(token in event for token in ("lookup", "read", "query", "check")):
            return "PRESENT", "readback"

    enabled = _lookup(fields, "enabled", "active", "is_enabled", "connector_enabled").casefold()
    restore = _lookup(fields, "restore_allowed", "restore_access", "can_restore", "restorable").casefold()
    if category == "DATA_FLOW" and enabled:
        if enabled in {"true", "1", "yes", "enabled", "active"}:
            return "ACTIVE", "readback"
        if enabled in {"false", "0", "no", "disabled", "inactive"}:
            return "DISABLED", "readback"
    if category == "BACKUP_ARCHIVE" and restore:
        if restore in {"true", "1", "yes", "allowed", "restorable"}:
            return "ACTIVE", "readback"
        if restore in {"false", "0", "no", "blocked", "unavailable"}:
            return "BLOCKED", "readback"

    if explicit in {"present", "active", "enabled", "redacted", "anonymized", "retained", "blocked", "disabled"}:
        if explicit == "retained":
            return "PRESENT", "readback"
        return explicit.upper(), "readback"
    if any(token in event for token in ("delete", "remove", "redact", "anonymize", "purge", "sync", "restore")):
        # Workflow activity is a claim unless a state/readback field above established it.
        return "UNKNOWN", "claim"
    return default, "snapshot"


def _resource_identifiers(text: str, allow_ocr_spaces: bool = False) -> list[str]:
    """Find explicit resource-shaped identifiers without using them to infer category."""
    found: list[tuple[int, str]] = []
    pattern = re.compile(
        r"\b(?!user_)([a-z][a-z0-9]*(?:_[a-z0-9]+)*_\d+[a-z0-9_-]*)\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text or ""):
        token = match.group(1)
        if token.casefold().startswith(("tr_", "trace_")):
            continue
        found.append((match.start(), token))
    if allow_ocr_spaces:
        for match in re.finditer(r"\b(search|export)\s+(\d{2,}[a-z0-9_-]*)\b", text or "", re.IGNORECASE):
            found.append((match.start(), f"{match.group(1)}_{match.group(2)}"))
    ordered: list[str] = []
    seen: set[str] = set()
    for _, token in sorted(found):
        normalized = token.casefold()
        if normalized not in seen:
            seen.add(normalized)
            ordered.append(token)
    return ordered


def _make_observation(
    source: EvidenceSource, fields: dict[str, Any], locator: str, source_kind: str,
    raw_text: str = "", table: str = "", default_state: str = "PRESENT",
) -> Observation:
    fields = dict(fields)
    fields.setdefault("evidence_origin", source.origin)
    if not _resource_id(fields):
        referenced_resource = _referenced_resource_id(raw_text)
        if not referenced_resource:
            resource_ids = _resource_identifiers(raw_text)
            if len(resource_ids) == 1:
                referenced_resource = resource_ids[0]
        if referenced_resource:
            fields["resource_id"] = referenced_resource
    if not _lookup(fields, "system_id", "origin_system", "system", "service", "service_name", "function", "data_store"):
        origin_system = _source_system_hint(source.origin)
        if origin_system:
            fields["system_id"] = origin_system
    category = infer_category(fields, table=table, source_kind=source_kind)
    if not category:
        event = _lookup(fields, "event_type", "event", "operation", "action").casefold()
        if any(token in event for token in ("connector", "sync", "import", "data_flow")) or _lookup(fields, "enabled", "is_enabled"):
            category = "DATA_FLOW"
        elif any(token in event for token in ("restore", "backup", "archive")) or _lookup(fields, "restore_allowed", "can_restore"):
            category = "BACKUP_ARCHIVE"
    system = _system_id(fields, table=table)
    resource = _resource_id(fields)
    scope = _lookup(fields, "scope_id", "replica_id", "region", "snapshot_scope", "database")
    if not scope and table == "customer_profiles_failover_replica":
        scope = "failover_replica"
    observed = None
    for key in TIME_KEYS:
        observed = maybe_instant(_lookup(fields, key))
        if observed is not None:
            break
    observed_at = observed or source.captured_at
    state, proof_kind = _observation_state(fields, category, default=default_state)
    trace_id = _lookup(fields, "trace_id", "request_id", "requestid", "correlation_id", "correlationid")
    return Observation(
        evidence_id=source.evidence_id,
        locator=locator,
        available_at=source.captured_at,
        observed_at=observed_at,
        system_id=system,
        resource_id=resource,
        scope_id=scope,
        category=category,
        state=state,
        fields=fields,
        source_kind=source_kind,
        proof_kind=proof_kind,
        scope_complete=_scope_complete(fields),
        raw_text=raw_text[:8000],
        trace_id=trace_id,
    )


def _referenced_resource_id(text: str) -> str:
    """Extract only identifiers explicitly labeled as a record/reference in prose."""
    patterns = (
        r"\b(?:support\s+)?reference\s+[A-Za-z0-9-]+\s*/\s*([A-Za-z][A-Za-z0-9_-]*_\d+)\b",
        r"\bevent\s+reference\s+((?:audit_record|security_record)_\d+)\b",
        r"\bstatement\s+([A-Z]{2,}[-_][A-Za-z0-9-]+)\b",
        r"\braw\s+(?:document|event|record)\s*[-:]\s*((?:account|search|analytics|support|backup|export|data_flow|tombstone|audit_record)_\d+)\b",
        r"\b(?:resource|record|ticket|attachment)\s+(?:id|reference|ref|number)\s*[:#]\s*([A-Za-z][A-Za-z0-9_-]*[_-]\d+)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _structured_text_rows(
    source: EvidenceSource,
    text: str,
    source_kind: str,
    locator_prefix: str,
) -> list[Observation]:
    """Split explicitly structured pipe-delimited evidence into source-located rows."""
    observations: list[Observation] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        normalized_line = line.strip().lstrip("-*• ").strip()
        cells = [cell.strip() for cell in normalized_line.split("|")]
        if len(cells) == 6 and re.fullmatch(
            r"\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)?", cells[0]
        ):
            observed_at, system_id, resource_id, category, raw_state, subject = cells
            state = raw_state.strip().upper().replace(" ", "_")
            state_map = {
                "NOT_FOUND": "ABSENT", "NOTFOUND": "ABSENT", "MISSING": "ABSENT",
                "FOUND": "PRESENT", "IDENTIFIABLE": "PRESENT", "RETAINED": "PRESENT",
            }
            normalized_state = state_map.get(state, state)
            fields: dict[str, Any] = {
                "observed_at": observed_at,
                "system_id": system_id,
                "resource_id": resource_id,
                "data_category": category,
                "record_state": normalized_state,
                "subject_reference": subject,
            }
            if state == "IDENTIFIABLE":
                fields["identifiers_exposed"] = "YES"
            item = _make_observation(
                source, fields, f"{locator_prefix}:line:{line_no}", source_kind, line,
            )
            if state in {"NOT_FOUND", "NOTFOUND", "MISSING"}:
                item.state = "ABSENT"
                item.proof_kind = "readback"
            observations.append(item)
            continue

        # Legal retention registers commonly present one record per pipe row.
        # Only accept a stable order ID, an exact internal subject ID, and an
        # explicit retain-until phrase; prose elsewhere remains unstructured.
        if len(cells) == 7 and re.fullmatch(r"ORD-[A-Za-z0-9-]+", cells[0]) and re.fullmatch(r"user_[A-Za-z0-9-]+", cells[1], re.IGNORECASE) and re.match(r"retain\s+until\s+", cells[5], re.IGNORECASE):
            retention_until = re.sub(r"^retain\s+until\s+", "", cells[5], flags=re.IGNORECASE).strip()
            fields = {
                "resource_id": cells[0],
                "subject_reference": cells[1],
                "record_type": "LEGAL_HOLD_RECORD",
                "record_state": "PRESENT",
                "retention_reason": cells[2],
                "record_date": cells[3],
                "amount": cells[4],
                "retention_until": retention_until,
                "retention_owner": cells[6],
            }
            observations.append(_make_observation(
                source, fields, f"{locator_prefix}:line:{line_no}", source_kind, line,
            ))
    return observations


def _json_records(document: Any) -> Iterable[tuple[str, dict[str, Any], str]]:
    """Yield record objects while carrying scalar parent context into nested rows."""
    containers = {"records", "snapshots", "service_exports", "events", "rows", "documents", "resources", "exports", "jobs"}
    record_markers = {"resource_id", "record_id", "user_id", "subject_reference", "customer_reference", "record_type", "event_type"}

    def walk(value: Any, inherited: dict[str, Any], pointer: str) -> Iterable[tuple[str, dict[str, Any], str]]:
        if isinstance(value, list):
            for i, child in enumerate(value):
                yield from walk(child, inherited, f"{pointer}[{i}]")
            return
        if not isinstance(value, dict):
            return
        context = dict(inherited)
        for key, child in value.items():
            if not isinstance(child, (dict, list)):
                context[key] = child
        own = _flat_fields(value)
        # A wrapper containing `records: [...]` also flattens every child's
        # `user_id`/`record_id` through _flat_fields. Only direct keys identify
        # this object as a record; otherwise the wrapper would become a false
        # aggregate observation that merges unrelated resources and provenance.
        own_keys = {str(key).split(".")[-1].lower() for key in value}
        if own_keys & record_markers:
            merged = dict(inherited)
            merged.update(own)
            yield pointer or "$", merged, json.dumps(value, ensure_ascii=False, default=str)
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                path = f"{pointer}.{key}" if pointer else f"$.{key}"
                yield from walk(child, context, path)

    yield from walk(document, {}, "$")


def _json_source(source: EvidenceSource, path: Path) -> list[Observation]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    observations: list[Observation] = []
    for locator, fields, raw in _json_records(document):
        if not fields:
            continue
        # Service-keyed JSON exports often omit a repeated system_id on every
        # child row. The nearest explicit service/platform/system key in the
        # JSON pointer is still participant-visible source provenance.
        path_parts = re.findall(r"\.([A-Za-z][A-Za-z0-9_-]*)", locator)
        path_system = next((
            part for part in reversed(path_parts)
            if part.casefold().endswith(("_service", "_platform", "_system"))
        ), "")
        if path_system and not _lookup(fields, "system_id", "origin_system", "system", "service", "service_name"):
            fields["system_id"] = path_system
        observations.append(_make_observation(source, fields, locator, "json", raw))
    if not observations:
        fields = _flat_fields(document)
        observations.append(_make_observation(source, fields, "$", "json", json.dumps(document, ensure_ascii=False, default=str)))
    return observations


def _parse_log_line(line: str) -> tuple[str, dict[str, Any]]:
    timestamp_match = re.match(r"^\s*(\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)?)\s+", line)
    timestamp = timestamp_match.group(1) if timestamp_match else ""
    rest = line[timestamp_match.end():] if timestamp_match else line
    parsed: dict[str, Any] = {}

    def parse_pairs(value: str) -> None:
        try:
            tokens = shlex.split(value, posix=True)
        except ValueError:
            tokens = value.split()
        for token in tokens:
            if "=" in token:
                key, item = token.split("=", 1)
                parsed[key] = item

    # Pipe-delimited operations stream: timestamp | level | service | trace | event | key=value...
    if rest.lstrip().startswith("|"):
        cells = [cell.strip() for cell in rest.split("|")]
        if cells and not cells[0]:
            cells = cells[1:]
        if len(cells) >= 4:
            parsed.update({"level": cells[0], "service": cells[1], "trace_id": cells[2], "event": cells[3]})
            parse_pairs(" ".join(cells[4:]))
            if timestamp:
                parsed.setdefault("timestamp", timestamp)
            return timestamp, _flat_fields(parsed)

    bracketed = re.match(
        r"^\s*\[(?P<level>[^\]]+)\]\s*\[(?P<service>[^\]]+)\]\s*\[(?P<trace>[^\]]+)\]\s*(?P<event>[A-Za-z][A-Za-z0-9_.-]*)\s*:\s*(?P<message>.*)$",
        rest,
    )
    if bracketed:
        parsed.update({
            "level": bracketed.group("level"),
            "service": bracketed.group("service"),
            "trace_id": bracketed.group("trace"),
            "event": bracketed.group("event"),
        })
        parse_pairs(bracketed.group("message"))
        if timestamp:
            parsed.setdefault("timestamp", timestamp)
        return timestamp, _flat_fields(parsed)

    # RFC 5424-style syslog envelope: <PRI>VERSION HOST APP PROCID MSGID SD MSG.
    syslog = re.match(
        r"^\s*<\d+>\d+\s+\S+\s+(?P<service>\S+)\s+(?P<trace>\S+)\s+\S+\s+\S+\s+(?P<message>.*)$",
        rest,
    )
    if syslog:
        parsed["service"] = syslog.group("service")
        parsed["trace_id"] = syslog.group("trace")
        parse_pairs(syslog.group("message"))
        if timestamp:
            parsed.setdefault("timestamp", timestamp)
        return timestamp, _flat_fields(parsed)

    json_start = rest.find("{")
    if json_start >= 0:
        try:
            obj = json.loads(rest[json_start:])
            if isinstance(obj, dict):
                parsed.update(obj)
                parsed.setdefault("timestamp", timestamp)
                return timestamp, _flat_fields(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

    parse_pairs(rest)
    if not parsed.get("message"):
        for token in rest.split():
            if "=" not in token and token:
                parsed.setdefault("message", token)
                break
    # Some collector exports place all structured fields inside a quoted message.
    nested = parsed.get("message")
    if isinstance(nested, str) and "=" in nested:
        try:
            for token in shlex.split(nested, posix=True):
                if "=" in token:
                    key, value = token.split("=", 1)
                    parsed.setdefault(key, value)
        except ValueError:
            pass
    if not _lookup(parsed, "service", "system_id") and _lookup(parsed, "function"):
        parsed["service"] = _lookup(parsed, "function")
    if not _lookup(parsed, "trace_id"):
        request_id = _lookup(parsed, "requestId", "requestid", "correlationId")
        if request_id:
            parsed["trace_id"] = request_id
    if timestamp:
        parsed.setdefault("timestamp", timestamp)
    return timestamp, _flat_fields(parsed)


def _log_source(source: EvidenceSource, path: Path) -> list[Observation]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    parsed_lines: list[tuple[int, str, dict[str, Any]]] = []
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        _, fields = _parse_log_line(line)
        parsed_lines.append((line_no, line, fields))

    # Preserve identity-bearing start lines and resource-bearing completion lines together.
    traces: dict[str, dict[str, Any]] = defaultdict(dict)
    for _, _, fields in parsed_lines:
        trace = _lookup(fields, "trace_id", "request_id", "requestid", "correlation_id", "correlationid")
        if trace:
            traces[trace].update({k: v for k, v in fields.items() if v not in (None, "")})

    export_expected: dict[str, int] = {}
    export_actual: dict[str, int] = {}
    export_dropped: dict[str, int] = {}
    for _, _, fields in parsed_lines:
        event = _lookup(fields, "event", "event_type").casefold()
        trace = _lookup(fields, "trace_id", "request_id", "requestid", "correlation_id", "correlationid") or "file"
        if event == "export_started":
            for key in ("expected_source_events", "target_count", "queries", "expected_records"):
                value = _lookup(fields, key)
                if value.isdigit():
                    export_expected[trace] = int(value)
                    break
        elif event == "export_completed":
            for key in ("actual_source_events", "source_events", "queries", "actual_records"):
                value = _lookup(fields, key)
                if value.isdigit():
                    export_actual[trace] = int(value)
                    break
            for key in ("dropped", "dropped_events", "dropped_records"):
                value = _lookup(fields, key)
                if value.isdigit():
                    export_dropped[trace] = int(value)
                    break

    complete_by_trace: dict[str, bool] = {}
    for trace in set(export_expected) | set(export_actual) | set(export_dropped):
        has_finish = trace in export_actual
        counts_match = trace not in export_expected or export_actual.get(trace) == export_expected[trace]
        no_drops = export_dropped.get(trace, 0) == 0
        complete_by_trace[trace] = has_finish and counts_match and no_drops

    out: list[Observation] = []
    for line_no, line, original in parsed_lines:
        trace = _lookup(original, "trace_id", "request_id", "requestid", "correlation_id", "correlationid")
        fields = dict(traces.get(trace, {})) if trace else {}
        fields.update(original)
        if trace:
            fields.setdefault("trace_id", trace)
        if trace in complete_by_trace:
            fields["scope_complete"] = complete_by_trace[trace]
        else:
            # File-level export completion markers are common in older log formats.
            file_complete = any(complete_by_trace.values()) if complete_by_trace else None
            if file_complete is not None:
                fields["scope_complete"] = file_complete
        event = _lookup(fields, "event", "event_type").casefold()
        if not event and not _resource_id(fields):
            continue
        observation = _make_observation(source, fields, f"line:{line_no}", "log", line)
        if event.endswith("_started") or event in {"export_started", "batch_started"}:
            observation.proof_kind = "claim"
            if observation.state == "PRESENT":
                observation.state = "UNKNOWN"
        if event.endswith("_completed") and any(key in fields for key in ("rows", "http_status", "status_code", "enabled", "restore_allowed")):
            observation.proof_kind = "readback"
        out.append(observation)
    return out


def _sqlite_authorizer(action: int, arg1: str | None, arg2: str | None, db: str | None, trigger: str | None) -> int:
    allow = {
        sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_INSERT, sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ, sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TEMP_TABLE, sqlite3.SQLITE_CREATE_TEMP_INDEX,
        sqlite3.SQLITE_REINDEX,
    }
    if action in allow:
        return sqlite3.SQLITE_OK
    # SQLite implements CREATE TABLE/INDEX by updating sqlite_master. Permit
    # only that internal catalog update; evidence scripts cannot mutate rows.
    if action == sqlite3.SQLITE_UPDATE and (arg1 or "").lower() == "sqlite_master":
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_PRAGMA and (arg1 or "").lower() == "foreign_keys" and (arg2 or "").upper() in {"", "ON", "1"}:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or arg1 or "").lower() not in {"load_extension"}:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _sql_source(source: EvidenceSource, path: Path) -> list[Observation]:
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError(f"{source.evidence_id}: SQL snapshot exceeds 32 MiB safety limit")
    sql = path.read_text(encoding="utf-8-sig", errors="strict")
    conn = sqlite3.connect(":memory:")
    conn.enable_load_extension(False)
    conn.set_authorizer(_sqlite_authorizer)
    try:
        conn.executescript(sql)
        conn.set_authorizer(None)
        conn.execute("PRAGMA query_only=ON")
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        scope_rows: list[dict[str, Any]] = []
        if "snapshot_scope" in tables:
            names = [row[1] for row in conn.execute('PRAGMA table_info("snapshot_scope")')]
            if conn.execute('SELECT COUNT(*) FROM "snapshot_scope"').fetchone()[0] > 1000:
                raise ValueError(f"{source.evidence_id}: snapshot_scope exceeds 1000 rows")
            scope_rows = [dict(zip(names, row)) for row in conn.execute('SELECT * FROM "snapshot_scope" LIMIT 1000')]
        scopes_by_origin: dict[str, dict[str, Any]] = {}
        for scope_row in scope_rows:
            origin = str(scope_row.get("origin_system", "") or "").strip()
            if origin:
                scopes_by_origin[origin.casefold()] = scope_row

        out: list[Observation] = []
        for table in tables:
            if table.startswith("sqlite_") or table == "snapshot_scope":
                continue
            quoted = '"' + table.replace('"', '""') + '"'
            names = [row[1] for row in conn.execute(f"PRAGMA table_info({quoted})")]
            if conn.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0] > 100000:
                raise ValueError(f"{source.evidence_id}: table {table} exceeds 100000 rows")
            for index, row in enumerate(conn.execute(f"SELECT * FROM {quoted} LIMIT 100000")):
                fields = dict(zip(names, row))
                origin = _lookup(_flat_fields(fields), "origin_system", "source_system", "system")
                if not origin:
                    mapped = _system_id({}, table=table)
                    origin = mapped
                context = scopes_by_origin.get(origin.casefold(), {})
                scoped_fields = {str(key): value for key, value in context.items() if str(key).lower() != "captured_at"}
                scoped_fields.update(fields)
                if context.get("captured_at") and not _lookup(_flat_fields(scoped_fields), "observed_at", "recorded_at", "updated_at", "timestamp"):
                    scoped_fields["snapshot_captured_at"] = context["captured_at"]
                fields = scoped_fields
                nested = fields.get("record_json")
                raw = ""
                if isinstance(nested, str) and nested.strip():
                    try:
                        parsed = json.loads(nested)
                        if isinstance(parsed, dict):
                            fields.update(_flat_fields(parsed))
                            raw = nested
                    except json.JSONDecodeError:
                        raw = nested
                fields["table"] = table
                category = infer_category(fields, table=table, source_kind="sql")
                observation = _make_observation(source, _flat_fields(fields), f"table:{table}:row:{index + 1}", "sql", raw, table=table)
                if category:
                    observation.category = category
                out.append(observation)
        return out
    finally:
        conn.close()


def _ocr_bytes(image_bytes: bytes) -> str:
    executable = shutil.which("tesseract")
    if not executable:
        raise RuntimeError("Tesseract is required to OCR image evidence")
    result = subprocess.run(
        [executable, "stdin", "stdout", "--psm", "6"], input=image_bytes,
        capture_output=True, timeout=60, check=False,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Tesseract failed: {message}")
    return result.stdout.decode("utf-8", errors="replace")


def _text_source(source: EvidenceSource, path: Path, source_kind: str = "text") -> list[Observation]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    rows = _structured_text_rows(source, text, source_kind, "text")
    if rows:
        return rows
    fields = {"text": text, "source": source.origin, "file_name": path.name}
    return [_make_observation(source, fields, "text:1", source_kind, text)]


def _pdf_source(source: EvidenceSource, path: Path) -> list[Observation]:
    import fitz

    out: list[Observation] = []
    document = fitz.open(path)
    try:
        for page_no, page in enumerate(document, 1):
            text = page.get_text("text") or ""
            if len(text.strip()) < 20:
                text = _ocr_bytes(page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).tobytes("png"))
            rows = _structured_text_rows(source, text, "pdf", f"page:{page_no}")
            if rows:
                out.extend(rows)
                continue
            record_type = _record_type_from_text(f"{text} {path.name} {source.origin}")
            fields = {"document_text": text, "page_number": page_no, "document_name": path.name, "record_type": record_type}
            out.append(_make_observation(source, fields, f"page:{page_no}", "pdf", text))
    finally:
        document.close()
    return out


def _record_type_from_text(text: str) -> str:
    normalized = re.sub(r"[_-]+", " ", text.casefold())
    for token, category in (
        ("customer download center", "USER_EXPORT"), ("data exports", "USER_EXPORT"),
        ("customer operations", "USER_PROFILE"), ("customer search", "SEARCH_INDEX_ENTRY"),
        ("customer statement", "USER_PROFILE"),
        ("search console", "SEARCH_INDEX_ENTRY"), ("pulse analytics", "ANALYTICS_PROFILE"),
        ("helpline console", "SUPPORT_MESSAGE"), ("sentinel", "SECURITY_AUDIT_LOG"),
        ("compliance journal", "SECURITY_AUDIT_LOG"),
        ("legal hold", "LEGAL_HOLD_RECORD"), ("retention register", "LEGAL_HOLD_RECORD"),
        ("security audit", "SECURITY_AUDIT_LOG"), ("audit journal", "SECURITY_AUDIT_LOG"),
        ("delivery correction attachment", "SUPPORT_ATTACHMENT"), ("support ticket", "SUPPORT_MESSAGE"),
        ("account history", "USER_PROFILE"), ("backup", "BACKUP_ARCHIVE"),
    ):
        if token in normalized:
            return category
    return ""


def _visual_resource_rows(source: EvidenceSource, text: str) -> list[Observation]:
    lines = text.splitlines()
    record_type = _record_type_from_text(text)
    rows: list[Observation] = []
    for line_no, line in enumerate(lines, 1):
        resource_ids = _resource_identifiers(line, allow_ocr_spaces=True)
        if record_type == "USER_EXPORT":
            export_ids = [value for value in resource_ids if value.casefold().startswith("export_")]
            if len(export_ids) == 1:
                # The export table labels its first ID column separately from
                # the customer_export_*.zip filename shown beside it.
                resource_ids = export_ids
        emails = re.findall(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}", line, re.IGNORECASE)
        subjects = re.findall(r"\buser_\d+\b", line, re.IGNORECASE)
        if len(resource_ids) != 1 or not (emails or subjects):
            continue
        fields: dict[str, Any] = {"resource_id": resource_ids[0]}
        if record_type:
            fields["record_type"] = record_type
        if len(emails) == 1:
            fields["email"] = emails[0]
        if len(subjects) == 1:
            fields["subject_reference"] = subjects[0]
        rows.append(_make_observation(
            source, fields, f"image:ocr:line:{line_no}", "image", line,
        ))

    # Some admin consoles show the selected row's raw document/event details in
    # a separate pane. Bind that pane to its explicit selected resource ID.
    selected = re.search(
        r"\braw\s+(?:document|event|record)\s*[-:]\s*((?:account|search|analytics|support|backup|export|data_flow|tombstone|audit_record)_\d+)\b",
        text, re.IGNORECASE,
    )
    if selected:
        details = text[selected.end():]
        emails = re.findall(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}", details, re.IGNORECASE)
        subjects = re.findall(r"\buser_\d+\b", details, re.IGNORECASE)
        if len(emails) == 1 or len(subjects) == 1:
            fields = {"resource_id": selected.group(1)}
            if record_type:
                fields["record_type"] = record_type
            if len(emails) == 1:
                fields["email"] = emails[0]
            if len(subjects) == 1:
                fields["subject_reference"] = subjects[0]
            rows.append(_make_observation(
                source, fields, "image:ocr:selected", "image", details,
            ))

    if rows:
        return rows

    # A single visible resource plus a single visible subject is an unambiguous
    # page-level record even when OCR split its fields over adjacent lines.
    resource_ids = _resource_identifiers(text, allow_ocr_spaces=True)
    emails = re.findall(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)
    subjects = re.findall(r"\buser_\d+\b", text, re.IGNORECASE)
    if len(resource_ids) == 1 and len(emails) + len(subjects) == 1:
        fields = {"resource_id": resource_ids[0]}
        if record_type:
            fields["record_type"] = record_type
        if emails:
            fields["email"] = emails[0]
        if subjects:
            fields["subject_reference"] = subjects[0]
        return [_make_observation(source, fields, "image:ocr", "image", text)]
    return []


def _image_source(source: EvidenceSource, path: Path) -> list[Observation]:
    text = _ocr_bytes(path.read_bytes())
    rows = _structured_text_rows(source, text, "image", "image:ocr")
    if rows:
        return rows
    visual_rows = _visual_resource_rows(source, text)
    if visual_rows:
        return visual_rows
    fields = {"image_text": text, "image_name": path.name, "record_type": _record_type_from_text(text)}
    return [_make_observation(source, fields, "image:ocr", "image", text)]


def load_manifest(dataset: Path) -> list[EvidenceSource]:
    rows = read_csv(dataset / "evidence_files.csv")
    sources: list[EvidenceSource] = []
    for row in rows:
        relative = Path(row["file_path"])
        target = (dataset / relative).resolve()
        if not path_is_within(target, dataset) or not target.is_file():
            raise ValueError(f"{row['file_id']}: unsafe or missing evidence path")
        sources.append(EvidenceSource(
            evidence_id=row["file_id"],
            path=row["file_path"],
            origin=row.get("origin", ""),
            captured_at=parse_instant(row["captured_at"]),
        ))
    return sources


def extract_sources(dataset: Path) -> list[Observation]:
    observations: list[Observation] = []
    for source in load_manifest(dataset):
        path = (dataset / source.path).resolve()
        suffix = path.suffix.lower()
        if suffix == ".json":
            batch = _json_source(source, path)
        elif suffix == ".sql":
            batch = _sql_source(source, path)
        elif suffix == ".log":
            batch = _log_source(source, path)
        elif suffix == ".pdf":
            batch = _pdf_source(source, path)
        elif suffix == ".png":
            batch = _image_source(source, path)
        elif suffix == ".txt":
            batch = _text_source(source, path)
        else:
            raise ValueError(f"{source.evidence_id}: unsupported evidence format {suffix}")
        observations.extend(batch)
    return observations


def extract_activity(dataset: Path) -> list[Observation]:
    rows = read_csv(dataset / "system_activity.csv")
    observations: list[Observation] = []
    for row in rows:
        event_time = parse_instant(row["event_time"])
        details = row.get("details", "")
        fields: dict[str, Any] = dict(row)
        try:
            detail_obj = json.loads(details)
            if isinstance(detail_obj, dict):
                fields.update(_flat_fields(detail_obj))
        except (json.JSONDecodeError, TypeError):
            for token in re.findall(r"([A-Za-z_][\w.-]*)=([^,;\s]+)", details):
                fields.setdefault(token[0], token[1].strip('"\''))
        fields["event_time"] = event_time.isoformat()
        fields["event_type"] = row.get("event_type", "")
        source = EvidenceSource(row["activity_id"], "system_activity.csv", "system_activity", event_time)
        observation = _make_observation(source, _flat_fields(fields), f"activity:{row['activity_id']}", "activity", details)
        event = row.get("event_type", "").casefold()
        if "check_data_flow" in event or "check_restore_access" in event or "readback" in event:
            observation.proof_kind = "readback"
        elif event.startswith("link_resource_identity"):
            observation.proof_kind = "identity_link"
        else:
            observation.proof_kind = "claim"
            if observation.state == "PRESENT":
                observation.state = "UNKNOWN"
        observations.append(observation)
    return observations
