import sys
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from audit_agent.extractors import (
    _json_records,
    _json_source,
    _make_observation,
    _parse_log_line,
    _record_type_from_text,
    _structured_text_rows,
    _visual_resource_rows,
)
from audit_agent.types import EvidenceSource


class JsonExtractionTests(unittest.TestCase):
    def test_failover_table_keeps_logical_system_and_physical_scope(self):
        source = EvidenceSource("evidence-test", "database.sql", "sql_dump", datetime(2026, 9, 1, tzinfo=timezone.utc))
        item = _make_observation(
            source,
            {"resource_id": "account_005", "user_id": "user_5", "record_type": "USER_PROFILE"},
            "table:customer_profiles_failover_replica:row:1",
            "sql",
            table="customer_profiles_failover_replica",
        )
        self.assertEqual(item.system_id, "account_service")
        self.assertEqual(item.scope_id, "failover_replica")

    def test_customer_statement_uses_metadata_to_avoid_tombstone_guess(self):
        self.assertEqual(
            _record_type_from_text("NORTHSTAR SHOP - CUSTOMER STATEMENT account_history_report_20260718.pdf account_history_service"),
            "USER_PROFILE",
        )

    def test_record_container_does_not_create_merged_parent_observation(self):
        document = {
            "captured_at": "2026-02-20T12:00:00Z",
            "records": [
                {"record_id": "primary-1", "user_id": "subject-1", "data_category": "USER_PROFILE"},
                {"record_id": "replica-1", "user_id": "subject-1", "data_category": "USER_PROFILE"},
            ],
        }
        records = list(_json_records(document))
        self.assertEqual(len(records), 2)
        self.assertEqual({row[1]["record_id"] for row in records}, {"primary-1", "replica-1"})

    def test_service_keyed_json_path_supplies_grounded_system_id(self):
        document = {
            "captured_at": "2026-02-20T12:00:00Z",
            "service_exports": {
                "search_service": {
                    "records": [{
                        "record_id": "document-1", "user_id": "subject-1",
                        "data_category": "SEARCH_INDEX_ENTRY", "state": "PRESENT",
                    }]
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            source = EvidenceSource("evidence-test", "evidence.json", "test_service_export", datetime(2026, 2, 20, tzinfo=timezone.utc))
            observations = _json_source(source, path)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].system_id, "search_service")
        self.assertEqual(observations[0].resource_id, "document-1")

    def test_system_like_manifest_origin_fills_missing_system_id(self):
        document = {
            "captured_at": "2026-02-20T12:00:00Z",
            "records": [{"record_id": "ticket-1", "user_id": "subject-1", "data_category": "SUPPORT_MESSAGE"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            source = EvidenceSource("evidence-test", "evidence.json", "support_platform", datetime(2026, 2, 20, tzinfo=timezone.utc))
            observations = _json_source(source, path)
        self.assertEqual(observations[0].system_id, "support_platform")

    def test_data_store_is_used_as_the_scoped_system(self):
        document = {
            "snapshots": [{
                "data_store": "identity_service",
                "records": [{"resource_id": "tombstone-1", "subject_reference": "user-1", "record_type": "ACCOUNT_TOMBSTONE"}],
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            source = EvidenceSource("evidence-test", "evidence.json", "records_bundle", datetime(2026, 2, 20, tzinfo=timezone.utc))
            observations = _json_source(source, path)
        self.assertEqual(observations[0].system_id, "identity_service")

    def test_logical_source_system_precedes_replica_service(self):
        source = EvidenceSource("evidence-test", "support.log", "log_export", datetime(2026, 2, 20, tzinfo=timezone.utc))
        _, fields = _parse_log_line(
            '2026-02-20T12:00:00Z [INFO] [support_replica] [tr-1] '
            'support_record_read_completed: resource_id="support_002" rows="1" source="support_platform"'
        )
        item = _make_observation(source, fields, "line:1", "log", "")
        self.assertEqual(item.system_id, "support_platform")

    def test_manifest_origin_resolves_replica_service_to_logical_owner(self):
        source = EvidenceSource("evidence-test", "support.log", "support_platform", datetime(2026, 2, 20, tzinfo=timezone.utc))
        _, fields = _parse_log_line(
            '2026-02-20T12:00:00Z [INFO] [support_replica] [tr-1] '
            'support_record_read_completed: resource_id="support_002" rows="1" source="legacy_contact_index"'
        )
        item = _make_observation(source, fields, "line:1", "log", "")
        self.assertEqual(item.system_id, "support_platform")

    def test_deleted_customer_reference_collection_is_a_tombstone(self):
        source = EvidenceSource("evidence-test", "snapshot.json", "records_bundle", datetime(2026, 2, 20, tzinfo=timezone.utc))
        item = _make_observation(
            source,
            {"resource_id": "tombstone-2", "subject_reference": "user-2", "collection_name": "deleted_customer_references"},
            "row:1", "json",
        )
        self.assertEqual(item.category, "ACCOUNT_TOMBSTONE")

    def test_pipe_delimited_handover_rows_keep_row_provenance_and_state(self):
        source = EvidenceSource("evidence-test", "evidence.txt", "account_service", datetime(2026, 10, 1, 12, tzinfo=timezone.utc))
        text = "2026-10-01T12:00:00Z | account_service | account_3677 | USER_PROFILE | NOT_FOUND | y.tanaka32@gmail.com\n"
        observations = _structured_text_rows(source, text, "text", "text")
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertEqual(item.locator, "text:line:1")
        self.assertEqual((item.system_id, item.resource_id, item.category), ("account_service", "account_3677", "USER_PROFILE"))
        self.assertEqual((item.state, item.proof_kind), ("ABSENT", "readback"))
        self.assertEqual(item.fields["subject_reference"], "y.tanaka32@gmail.com")

    def test_pipe_delimited_retention_register_is_split_by_subject(self):
        source = EvidenceSource("evidence-test", "register.pdf", "legal_retention_service", datetime(2026, 5, 29, tzinfo=timezone.utc))
        text = "ORD-20264207 | user_12 | Tax correction | 09 May 2026 | EUR 72.40 | Retain until 09 May 2033 | ML\n"
        observations = _structured_text_rows(source, text, "pdf", "page:2")
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertEqual(item.locator, "page:2:line:1")
        self.assertEqual((item.system_id, item.resource_id, item.category), ("legal_retention_service", "ORD-20264207", "LEGAL_HOLD_RECORD"))
        self.assertEqual(item.fields["subject_reference"], "user_12")
        self.assertEqual(item.fields["retention_until"], "09 May 2033")

    def test_labeled_support_reference_supplies_only_the_explicit_resource(self):
        source = EvidenceSource("evidence-test", "attachment.pdf", "support_platform", datetime(2026, 9, 12, tzinfo=timezone.utc))
        text = "Support reference CS-4827 / support_001\nDelivery address correction\n"
        item = _make_observation(source, {"document_text": text, "record_type": "SUPPORT_ATTACHMENT"}, "page:1", "pdf", text)
        self.assertEqual(item.system_id, "support_platform")
        self.assertEqual(item.resource_id, "support_001")

    def test_event_reference_supplies_grounded_pdf_resource_id(self):
        source = EvidenceSource("evidence-test", "journal.pdf", "security_service", datetime(2026, 9, 5, tzinfo=timezone.utc))
        text = "COMPLIANCE JOURNAL\nEvent reference audit_record_003\nsubject reference user_03\n"
        item = _make_observation(source, {"document_text": text, "record_type": "SECURITY_AUDIT_LOG"}, "page:1", "pdf", text)
        self.assertEqual(item.system_id, "security_service")
        self.assertEqual(item.resource_id, "audit_record_003")

    def test_visual_export_rows_bind_ids_to_owner_emails_not_zip_names(self):
        source = EvidenceSource("evidence-test", "console.png", "export_service", datetime(2026, 6, 18, tzinfo=timezone.utc))
        text = "Customer Download Center Data exports\nExport ID File Owner Status\n2) export 1260 customer_export_1260.zip ingrid.dahl@outlook.com Ready\n"
        observations = _visual_resource_rows(source, text)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].resource_id, "export_1260")
        self.assertEqual(observations[0].fields["email"], "ingrid.dahl@outlook.com")
        self.assertEqual(observations[0].category, "USER_EXPORT")

    def test_visual_raw_document_panel_binds_its_selected_search_record(self):
        source = EvidenceSource("evidence-test", "search.png", "search_index_admin", datetime(2026, 9, 1, tzinfo=timezone.utc))
        text = "Search Console Customer Search\nRaw document - search_428\nemail g.silva76@gmail.com\ncustomer_reference user_13\n"
        observations = _visual_resource_rows(source, text)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].resource_id, "search_428")
        self.assertEqual(observations[0].fields["email"], "g.silva76@gmail.com")
        self.assertEqual(observations[0].system_id, "search_index_admin")

    def test_visual_single_profile_joins_adjacent_email_and_portal_origin(self):
        source = EvidenceSource("evidence-test", "account.png", "account_admin_portal", datetime(2026, 9, 26, tzinfo=timezone.utc))
        text = "Customer Operations\nUser account_5762\nemail haruka.s1838@zoho.com\n"
        observations = _visual_resource_rows(source, text)
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].resource_id, "account_5762")
        self.assertEqual(observations[0].system_id, "account_admin_portal")


class LogFormatExtractionTests(unittest.TestCase):
    def test_cloud_runtime_nested_message_preserves_function_and_request_id(self):
        line = '2026-06-08T09:57:22Z requestId=tr-4557555 level=DEBUG function=security_service message="instance=\\"security-6\\" resource_id=\\"audit_record_6863\\" event=\\"audit_record_read_completed\\" rows=\\"1\\""'
        _, fields = _parse_log_line(line)
        self.assertEqual((fields["service"], fields["trace_id"], fields["resource_id"], fields["event"]),
                         ("security_service", "tr-4557555", "audit_record_6863", "audit_record_read_completed"))

    def test_rfc5424_syslog_envelope_preserves_service_and_trace(self):
        line = '2026-03-25T08:53:47Z <15>1 node-4 security_service tr-2264439 - - level=DEBUG instance="security-2" resource_id="audit_record_123" event="audit_record_query_started" subject_ref="user_411"'
        _, fields = _parse_log_line(line)
        self.assertEqual((fields["service"], fields["trace_id"], fields["resource_id"], fields["subject_ref"]),
                         ("security_service", "tr-2264439", "audit_record_123", "user_411"))

    def test_pipe_delimited_operations_log_preserves_service_and_resource(self):
        line = '2026-02-03T05:57:51Z | DEBUG | account_service | tr-0668675 | profile_lookup_completed | instance="account-6" resource_id="account_1334" rows="1" http_status="200"'
        _, fields = _parse_log_line(line)
        self.assertEqual((fields["service"], fields["trace_id"], fields["resource_id"], fields["event"]),
                         ("account_service", "tr-0668675", "account_1334", "profile_lookup_completed"))

    def test_bracketed_application_log_preserves_control_flag(self):
        line = '2026-02-28T10:59:32Z [ERROR] [backup_service] [tr-3607990] restore_candidate_evaluated: resource_id="backup_7543" eligible="true" deletion_block="false"'
        _, fields = _parse_log_line(line)
        self.assertEqual((fields["service"], fields["trace_id"], fields["resource_id"], fields["deletion_block"]),
                         ("backup_service", "tr-3607990", "backup_7543", "false"))


if __name__ == "__main__":
    unittest.main()
