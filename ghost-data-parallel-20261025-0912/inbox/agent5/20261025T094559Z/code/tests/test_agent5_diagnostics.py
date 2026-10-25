import json
import sys
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from agent5_diagnostics import (
    render_report,
    score_rows,
    _retention_evidence_probe,
    _safe_validation_categories,
)


def step(number=1, operation="REPORT_REMAINING_RECORD", resource="fixture"):
    phase, state = {
        "REPORT_REMAINING_RECORD": ("FINDING", "PRESENT"),
        "VERIFY_RECORD_ABSENT": ("VERIFICATION", "ABSENT"),
        "VERIFY_RECORD_PRESENT": ("VERIFICATION", "PRESENT"),
    }[operation]
    return {
        "step_no": number,
        "phase": phase,
        "system_id": "fixture_system",
        "resource_id": resource,
        "operation": operation,
        "state": state,
        "evidence_id": "fixture_evidence",
    }


class Agent5DiagnosticsTests(unittest.TestCase):
    def test_metrics_count_exact_steps_and_positional_fields(self):
        gold = [{
            "case_id": "private_case_id",
            "deletion_status": "INCOMPLETE",
            "steps_json": json.dumps([step(), step(2, "VERIFY_RECORD_ABSENT", "second")]),
        }]
        predicted = [{
            "case_id": "private_case_id",
            "deletion_status": "INCOMPLETE",
            "steps_json": json.dumps([step(resource="different")]),
        }]
        result = score_rows(gold, predicted)
        self.assertEqual(result["step_true_positive"], 0)
        self.assertEqual(result["predicted_steps"], 1)
        self.assertEqual(result["gold_steps"], 2)
        self.assertEqual(result["field_total"], 14)
        self.assertEqual(result["field_matches"], 6)
        self.assertEqual(result["case_mismatches"], 1)
        self.assertIn(("missing step: VERIFY_RECORD_ABSENT", 1), result["top_patterns"])

    def test_operation_breakdown_is_multiset_based(self):
        gold = [{
            "case_id": "c",
            "deletion_status": "INCOMPLETE",
            "steps_json": json.dumps([step(), step(2)]),
        }]
        predicted = [{
            "case_id": "c",
            "deletion_status": "INCOMPLETE",
            "steps_json": json.dumps([step()]),
        }]
        by_name = {item["operation"]: item for item in score_rows(gold, predicted)["operations"]}
        self.assertEqual(by_name["REPORT_REMAINING_RECORD"]["gold"], 2)
        self.assertEqual(by_name["REPORT_REMAINING_RECORD"]["matched"], 1)
        self.assertEqual(by_name["REPORT_REMAINING_RECORD"]["missing"], 1)

    def test_retention_probe_reports_aggregate_exact_match_count(self):
        gold = [{
            "case_id": "private_case_id",
            "deletion_status": "COMPLETE",
            "steps_json": json.dumps([step(operation="VERIFY_RECORD_ABSENT")]),
        }]
        predicted = [{
            "case_id": "private_case_id",
            "deletion_status": "COMPLETE",
            "steps_json": json.dumps([{
                **step(operation="VERIFY_RECORD_PRESENT", resource="legal_retention_record"),
                "evidence_id": "citation",
            }]),
        }]
        result = score_rows(gold, predicted)
        self.assertEqual(result["retention_probe"], {"predicted": 1, "exact_matches": 0})

    def test_retention_evidence_probe_flags_unlinked_incomplete_check(self):
        row = {
            "case_id": "private_case_id",
            "deletion_status": "INCOMPLETE",
            "steps_json": json.dumps([{
                **step(operation="VERIFY_RECORD_PRESENT", resource="legal_retention_record"),
                "evidence_id": "",
            }]),
        }
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp)
            (dataset / "evidence_files.csv").write_text(
                "file_id,file_path,origin,captured_at\n", encoding="utf-8"
            )
            (dataset / "system_activity.csv").write_text(
                "activity_id,event_time\n", encoding="utf-8"
            )
            (dataset / "user_audit_log.csv").write_text(
                "audit_id,event_time\n", encoding="utf-8"
            )
            summary = _retention_evidence_probe([row], dataset)
        self.assertEqual(summary["candidates"], 1)
        self.assertEqual(summary["incomplete_without_same_resource_finding"], 1)
        self.assertEqual(summary["cited_pdfs"], 0)

    def test_report_and_validation_summary_omit_case_ids(self):
        categories = _safe_validation_categories(["private_case_id: invalid steps_json"])
        self.assertEqual(categories, Counter({"invalid steps_json": 1}))
        report = render_report(
            prediction_path=Path("predictions.csv"),
            report_started=datetime(2026, 10, 25, 9, 0, tzinfo=timezone.utc),
            before_mtime=datetime(2026, 10, 25, 8, 0, tzinfo=timezone.utc),
            before_hash="abc",
            after_mtime=datetime(2026, 10, 25, 8, 0, tzinfo=timezone.utc),
            after_hash="abc",
            prediction_rows=1,
            distinct_prediction_ids=1,
            matched_sample_rows=1,
            sample_rows=32,
            validation_categories=categories,
            metrics=None,
        )
        self.assertNotIn("private_case_id", report)
        self.assertIn("Prediction pre-existed evaluation: **yes**", report)
        self.assertIn("Validation failed", report)


if __name__ == "__main__":
    unittest.main()
