"""Create isolated, participant-authored synthetic cases for model E2E checks."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_evidence(folder: Path, filename: str, captured_at: str, records: list[dict[str, object]]) -> str:
    relative = f"evidence/{filename}"
    path = folder / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"captured_at": captured_at, "records": records}, indent=2), encoding="utf-8")
    return relative


def build(dataset: Path, policy_path: Path) -> None:
    if dataset.exists() and any(dataset.iterdir()):
        raise FileExistsError(f"refusing to overwrite a non-empty synthetic dataset: {dataset}")
    dataset.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(policy_path, dataset / "deletion_rules.csv")

    requests = [
        {
            "case_id": "custom-no-delete",
            "email": "deny@example.test",
            "requested_at": "2026-01-01T00:00:00Z",
            "reported_status": "Complete",
            "reported_at": "2026-01-03T00:00:00Z",
            "audit_at": "2026-02-01T00:00:00Z",
            "request_text": "Please send me a copy of my data. Do not delete my account or any personal information.",
        },
        {
            "case_id": "custom-old-alias-replica-flow",
            "email": "old-alias@example.test",
            "requested_at": "2026-01-01T00:00:00Z",
            "reported_status": "Complete",
            "reported_at": "2026-01-20T00:00:00Z",
            "audit_at": "2026-03-01T00:00:00Z",
            "request_text": "Delete my account and erase all personal information associated with it.",
        },
        {
            "case_id": "custom-compliant-tombstone-retained-log",
            "email": "retained@example.test",
            "requested_at": "2026-01-01T00:00:00Z",
            "reported_status": "Complete",
            "reported_at": "2026-01-20T00:00:00Z",
            "audit_at": "2026-03-01T00:00:00Z",
            "request_text": "Please permanently delete my account and personal data.",
        },
    ]
    identities = [
        {"user_id": "synthetic-deny", "name": "Synthetic Deny", "email": "deny@example.test", "phone": "", "email_hash": "", "updated_at": "2025-12-01T00:00:00Z"},
        {"user_id": "synthetic-alias", "name": "Synthetic Alias", "email": "new-alias@example.test", "phone": "", "email_hash": "", "updated_at": "2026-01-15T00:00:00Z"},
        {"user_id": "synthetic-retained", "name": "Synthetic Retained", "email": "retained@example.test", "phone": "", "email_hash": "", "updated_at": "2025-12-01T00:00:00Z"},
    ]
    audit = [{
        "audit_id": "custom-alias-change",
        "user_id": "synthetic-alias",
        "event_time": "2026-01-15T00:00:00Z",
        "field_name": "email",
        "old_value": "old-alias@example.test",
        "new_value": "new-alias@example.test",
    }]
    write_csv(dataset / "deletion_requests.csv", list(requests[0]), requests)
    write_csv(dataset / "user_identities.csv", list(identities[0]), identities)
    write_csv(dataset / "user_audit_log.csv", list(audit[0]), audit)
    write_csv(dataset / "system_activity.csv", ["activity_id", "event_time", "event_type", "source_system", "target_system", "resource_id", "reported_result", "details"], [])

    cutoff_capture = "2026-02-20T12:00:00Z"
    files = []
    examples: list[tuple[str, list[dict[str, object]]]] = [
        ("custom-no-delete.json", [{
            "data_category": "USER_PROFILE", "record_id": "profile-deny", "system_id": "account_service",
            "user_id": "synthetic-deny", "observed_state": "PRESENT", "scope_id": "primary",
            "observed_at": cutoff_capture,
        }]),
        ("custom-alias-state.json", [
            {
                "data_category": "USER_PROFILE", "record_id": "profile-primary", "system_id": "account_primary",
                "user_id": "synthetic-alias", "observed_state": "not_found", "event_type": "record_lookup_completed",
                "result_count": 0, "email": "old-alias@example.test", "scope_id": "primary",
                "scope_complete": True, "observed_at": cutoff_capture,
            },
            {
                "data_category": "USER_PROFILE", "record_id": "profile-replica", "system_id": "account_replica",
                "user_id": "synthetic-alias", "observed_state": "PRESENT", "email": "old-alias@example.test",
                "scope_id": "region-west", "scope_complete": True, "observed_at": cutoff_capture,
            },
            {
                "data_category": "DATA_FLOW", "event_type": "connector_subscription", "record_id": "sync-flow-1",
                "system_id": "integration_service", "user_id": "synthetic-alias", "enabled": True,
                "scope_id": "connector-west", "observed_at": cutoff_capture,
            },
        ]),
        ("custom-retained-records.json", [
            {
                "data_category": "ACCOUNT_TOMBSTONE", "record_id": "tombstone-1", "system_id": "account_service",
                "user_id": "synthetic-retained", "subject_reference": "synthetic-retained",
                "observed_state": "REDACTED", "name": None, "email": None, "phone": None,
                "email_hash": None, "identifiers_exposed": "NO", "account_deleted": True,
                "scope_id": "primary", "scope_complete": True, "observed_at": cutoff_capture,
            },
            {
                "data_category": "SECURITY_AUDIT_LOG", "record_id": "security-record-1", "system_id": "security_service",
                "user_id": "synthetic-retained", "observed_state": "PRESENT", "retention_period_status": "within_required_retention",
                "scope_id": "audit-ledger", "scope_complete": True, "observed_at": cutoff_capture,
            },
        ]),
    ]
    request_to_file = {"synthetic-deny": "custom-no-delete.json", "synthetic-alias": "custom-alias-state.json", "synthetic-retained": "custom-retained-records.json"}
    for filename, records in examples:
        relative = write_evidence(dataset, filename, cutoff_capture, records)
        user_id = next(key for key, value in request_to_file.items() if value == filename)
        files.append({"file_id": f"evidence-{user_id}", "file_path": relative, "origin": "synthetic fixture", "captured_at": cutoff_capture})
    write_csv(dataset / "evidence_files.csv", ["file_id", "file_path", "origin", "captured_at"], files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path(__file__).resolve().parents[2] / "dataset" / "deletion_rules.csv")
    args = parser.parse_args()
    build(args.dataset.resolve(), args.policy.resolve())
    print(f"created three synthetic cases under {args.dataset.resolve()}")


if __name__ == "__main__":
    main()
