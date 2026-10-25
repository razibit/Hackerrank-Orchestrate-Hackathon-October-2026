import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from audit_agent.datalab_ocr import DatalabExtractionError, DatalabOCR
from audit_agent.extractors import _pdf_source
from audit_agent.types import EvidenceSource


class Options:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeDatalabClient:
    def __init__(self, result=None, errors=()):
        self.result = result or SimpleNamespace(
            success=True,
            extraction_schema_json=json.dumps({
                "transcribed_text": "Evidence register",
                "transcribed_text_citations": ["/page/0/Text/1"],
                "transcribed_text_meta": {"extraction_status": "EXTRACTED"},
                "tables": [{"caption": "Records", "headers": ["resource_id", "user_id"], "rows": [["account_1", "user_1"]]}],
                "tables_citations": ["/page/0/Table/1"],
            }),
            json={"pages": [{"blocks": [{"type": "Table", "bbox": [0, 0, 100, 50]}]}]},
            markdown="Evidence register",
            parse_quality_score=4.8,
            page_count=1,
            cost_breakdown={"final_cost_cents": 2.0},
        )
        self.errors = list(errors)
        self.calls = []

    def extract(self, path, options):
        self.calls.append((path, options))
        if self.errors:
            error = self.errors.pop(0)
            raise error
        return self.result


class DatalabOCRTests(unittest.TestCase):
    def test_uses_high_accuracy_structured_extraction_and_preserves_citations(self):
        client = FakeDatalabClient()
        provider = DatalabOCR(client=client, options_type=Options)
        result = provider.extract_image(Path("page.png"))

        self.assertEqual(client.calls[0][1].kwargs["mode"], "accurate")
        self.assertEqual(client.calls[0][1].kwargs["extraction_mode"], "accurate")
        self.assertEqual(client.calls[0][1].kwargs["output_format"], "json")
        self.assertEqual(result["transcribed_text"], "Evidence register")
        self.assertEqual(result["citations"]["transcribed_text_citations"], ["/page/0/Text/1"])
        self.assertEqual(result["field_metadata"]["transcribed_text_meta"]["extraction_status"], "EXTRACTED")
        self.assertEqual(result["layout_json"]["pages"][0]["blocks"][0]["type"], "Table")
        self.assertEqual(provider.usage_summary()["successful_requests"], 1)
        self.assertEqual(provider.usage_summary()["reported_cost_cents"], 2.0)

    def test_retries_network_errors_at_most_three_times(self):
        client = FakeDatalabClient(errors=(OSError("offline"), OSError("offline"), OSError("offline")))
        provider = DatalabOCR(client=client, options_type=Options)
        with self.assertRaises(DatalabExtractionError):
            provider.extract_image(Path("page.png"))
        summary = provider.usage_summary()
        self.assertEqual(len(client.calls), 3)
        self.assertEqual(summary["request_attempts"], 3)
        self.assertEqual(summary["failed_requests"], 3)
        self.assertEqual(summary["retries"], 2)

    def test_pdf_pages_are_rendered_to_png_and_sent_as_images(self):
        import fitz

        seen = []

        class ImageVerifier:
            def extract_image(self, image_path):
                from PIL import Image

                image_path = Path(image_path)
                with Image.open(image_path) as image:
                    seen.append((image_path.suffix, image.width, image.height))
                return {
                    "transcribed_text": "Customer operations account_1 user_1",
                    "tables": [], "citations": {}, "field_metadata": {},
                    "layout_json": {"pages": []}, "markdown": "",
                    "parse_quality_score": 4.5, "page_count": 1,
                }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "one-page.pdf"
            pdf = fitz.open()
            page = pdf.new_page(width=72, height=72)
            page.insert_text((5, 20), "Customer operations account_1 user_1")
            pdf.save(path)
            pdf.close()
            source = EvidenceSource("evidence-1", "one-page.pdf", "customer_operations", datetime(2026, 1, 1, tzinfo=timezone.utc))
            observations = _pdf_source(source, path, ImageVerifier())

        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][0], ".png")
        self.assertGreaterEqual(seen[0][1], 299)
        self.assertGreaterEqual(seen[0][2], 299)
        self.assertTrue(observations[0].locator.startswith("page:1:datalab"))
        self.assertEqual(observations[0].fields["ocr_provider"], "Datalab")


if __name__ == "__main__":
    unittest.main()
