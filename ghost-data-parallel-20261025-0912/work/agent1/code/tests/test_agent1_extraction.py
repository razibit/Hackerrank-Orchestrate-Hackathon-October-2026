import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from audit_agent.extractors import (  # noqa: E402
    _record_type_from_text,
    _structured_text_rows,
    infer_category,
)
from audit_agent.types import EvidenceSource  # noqa: E402


class RetentionRegisterExtractionTests(unittest.TestCase):
    def setUp(self):
        self.source = EvidenceSource(
            evidence_id="evidence_27",
            path="evidence/documents/legal_retention_register_20260529.pdf",
            origin="legal_retention_service",
            captured_at=datetime(2026, 5, 29, 8, tzinfo=timezone.utc),
        )

    def test_register_row_is_not_inferred_to_be_a_legal_hold(self):
        row = (
            "ORD-20264207 | user_12 | Tax correction | 09 May 2026 | EUR 72.40 | "
            "Retain until 09 May 2033 | ML"
        )

        observations = _structured_text_rows(self.source, row, "pdf", "page:2")

        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertEqual(item.category, "UNRESOLVED")
        self.assertEqual((item.state, item.proof_kind), ("PRESENT", "snapshot"))
        self.assertEqual((item.system_id, item.resource_id, item.scope_id), (
            "legal_retention_service", "ORD-20264207", ""
        ))
        self.assertEqual((item.evidence_id, item.locator), ("evidence_27", "page:2:line:1"))
        self.assertEqual(item.available_at, self.source.captured_at)
        self.assertEqual(item.observed_at, self.source.captured_at)
        self.assertIsNone(item.scope_complete)
        self.assertEqual(item.raw_text, row)

        # Keep source facts and the manifest path without synthesizing an
        # active-hold or readback field that the document does not contain.
        self.assertEqual(item.fields["source_path"], self.source.path)
        self.assertEqual(item.fields["record_type"], "RETENTION_REGISTER_ENTRY")
        self.assertEqual(item.fields["subject_reference"], "user_12")
        self.assertEqual(item.fields["retention_reason"], "Tax correction")
        self.assertEqual(item.fields["record_date"], "09 May 2026")
        self.assertEqual(item.fields["amount"], "EUR 72.40")
        self.assertEqual(item.fields["retention_until"], "09 May 2033")
        self.assertEqual(item.fields["retention_owner"], "ML")
        self.assertNotIn("record_state", item.fields)

    def test_document_heading_distinguishes_register_from_explicit_hold(self):
        register = _record_type_from_text(
            "DISPUTED ORDERS AND TAX RECORDS REGISTER "
            "legal_retention_register_20260529.pdf legal_retention_service"
        )
        legal_hold = _record_type_from_text("LEGAL HOLD NOTICE active hold case LH-4")

        self.assertEqual(register, "RETENTION_REGISTER_ENTRY")
        self.assertEqual(infer_category({"record_type": register}), "UNRESOLVED")
        self.assertEqual(legal_hold, "LEGAL_HOLD_RECORD")
        self.assertEqual(infer_category({"record_type": legal_hold}), "LEGAL_HOLD_RECORD")


if __name__ == "__main__":
    unittest.main()
