"""Structured, citation-bearing OCR through Datalab's accurate extraction API."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


EXTRACTOR_VERSION = "datalab-accurate-image-extraction-v1"
PARSE_MODE = "accurate"
EXTRACTION_MODE = "accurate"

PAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "transcribed_text": {
            "type": "string",
            "description": (
                "Faithfully transcribe all visible text on this page in reading order. "
                "Preserve line breaks and labels. Do not summarize, infer, normalize IDs, "
                "or add facts that are not visible."
            ),
        },
        "tables": {
            "type": "array",
            "description": "Every visible table, preserving row and column boundaries.",
            "items": {
                "type": "object",
                "properties": {
                    "caption": {"type": "string", "description": "Visible table title, or empty."},
                    "headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Visible column headers, in left-to-right order.",
                    },
                    "rows": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}},
                        "description": "Table cells, one array per row, in left-to-right order.",
                    },
                },
            },
        },
    },
}


class DatalabConfigurationError(RuntimeError):
    pass


class DatalabExtractionError(RuntimeError):
    pass


class DatalabOCR:
    """Synchronous page-image extractor with bounded retries and safe usage records."""

    def __init__(self, client: Any | None = None, options_type: Any | None = None):
        self._client = client
        self._options_type = options_type
        self.usage_records: list[dict[str, Any]] = []

    def _initialize(self) -> None:
        if self._client is not None and self._options_type is not None:
            return
        if not os.environ.get("DATALAB_API_KEY", "").strip():
            raise DatalabConfigurationError(
                "Set DATALAB_API_KEY in the process environment to extract PDF/image evidence"
            )
        try:
            from datalab_sdk import DatalabClient, ExtractOptions
        except ImportError as exc:
            raise DatalabConfigurationError(
                "Install code/requirements.txt to use Datalab document extraction"
            ) from exc
        self._client = DatalabClient()
        self._options_type = ExtractOptions

    @staticmethod
    def _parse_result(result: Any) -> dict[str, Any]:
        if getattr(result, "success", True) is False:
            raise DatalabExtractionError("Datalab reported an unsuccessful extraction")
        raw = getattr(result, "extraction_schema_json", None)
        if isinstance(raw, str):
            try:
                extraction = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise DatalabExtractionError("Datalab returned invalid structured JSON") from exc
        else:
            extraction = raw
        if not isinstance(extraction, dict):
            raise DatalabExtractionError("Datalab returned no structured extraction object")
        transcription = extraction.get("transcribed_text", "")
        tables = extraction.get("tables", [])
        if not isinstance(transcription, str) or not isinstance(tables, list):
            raise DatalabExtractionError("Datalab extraction did not match the requested schema")

        citations: dict[str, Any] = {}
        metadata: dict[str, Any] = {}

        def collect(node: Any, prefix: str = "") -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    path = f"{prefix}.{key}" if prefix else str(key)
                    if str(key).endswith("_citations"):
                        citations[path] = value
                    elif str(key).endswith("_meta"):
                        metadata[path] = value
                    else:
                        collect(value, path)
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    collect(value, f"{prefix}[{index}]")

        collect(extraction)
        layout = getattr(result, "json", None)
        if callable(layout):
            layout = None
        markdown = getattr(result, "markdown", None)
        return {
            "transcribed_text": transcription,
            "tables": tables,
            "citations": citations,
            "field_metadata": metadata,
            "layout_json": layout if isinstance(layout, (dict, list)) else None,
            "markdown": markdown if isinstance(markdown, str) else "",
            "parse_quality_score": getattr(result, "parse_quality_score", None),
            "page_count": getattr(result, "page_count", None),
            "cost_breakdown": getattr(result, "cost_breakdown", None),
        }

    def extract_image(self, image_path: Path) -> dict[str, Any]:
        self._initialize()
        options = self._options_type(
            page_schema=json.dumps(PAGE_SCHEMA, ensure_ascii=False),
            extraction_mode=EXTRACTION_MODE,
            mode=PARSE_MODE,
            output_format="json",
            save_checkpoint=False,
        )
        last_error: Exception | None = None
        for attempt in range(1, 4):
            started = time.monotonic()
            record: dict[str, Any] = {
                "provider": "Datalab",
                "operation": "structured_image_extraction",
                "parse_mode": PARSE_MODE,
                "extraction_mode": EXTRACTION_MODE,
                "attempt": attempt,
                "success": False,
                "elapsed_seconds": None,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "final_cost_cents": None,
            }
            try:
                result = self._client.extract(str(image_path), options=options)
                record["success"] = getattr(result, "success", True) is not False
                breakdown = getattr(result, "cost_breakdown", None)
                if isinstance(breakdown, dict):
                    cost = breakdown.get("final_cost_cents")
                    if isinstance(cost, (int, float)):
                        record["final_cost_cents"] = cost
                parsed = self._parse_result(result)
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                self.usage_records.append(record)
                return parsed
            except DatalabExtractionError:
                record["success"] = False
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                self.usage_records.append(record)
                raise
            except Exception as exc:
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                record["error_type"] = type(exc).__name__
                self.usage_records.append(record)
                last_error = exc
                response = getattr(exc, "response", None)
                status_code = getattr(exc, "status_code", None) or getattr(response, "status_code", None)
                try:
                    status_code = int(status_code) if status_code is not None else None
                except (TypeError, ValueError):
                    status_code = None
                retryable = status_code is None or status_code in {408, 429} or status_code >= 500
                if attempt >= 3 or not retryable:
                    break
                time.sleep(2 ** (attempt - 1))
        raise DatalabExtractionError(
            f"Datalab request failed after {len(self.usage_records)} recorded attempts"
        ) from last_error

    def usage_summary(self) -> dict[str, Any]:
        successful = [record for record in self.usage_records if record.get("success")]
        costs = [
            float(record["final_cost_cents"])
            for record in self.usage_records
            if isinstance(record.get("final_cost_cents"), (int, float))
        ]
        return {
            "provider": "Datalab",
            "model_name": "provider-managed accurate extraction (exact model ID not exposed by SDK result)",
            "parse_mode": PARSE_MODE,
            "extraction_mode": EXTRACTION_MODE,
            "request_attempts": len(self.usage_records),
            "successful_requests": len(successful),
            "failed_requests": len(self.usage_records) - len(successful),
            "retries": sum(1 for record in self.usage_records if int(record.get("attempt", 1)) > 1),
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "reported_cost_cents": sum(costs) if costs else None,
            "elapsed_seconds": round(
                sum(float(record.get("elapsed_seconds") or 0) for record in self.usage_records), 3
            ),
            "usage_records": self.usage_records,
        }
