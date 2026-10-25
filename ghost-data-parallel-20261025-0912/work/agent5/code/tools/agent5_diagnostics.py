"""Independent, non-inference diagnostics for an existing partial sample CSV."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contract import FIELDS, STEP_FIELDS, OPERATIONS, evidence_times, read_csv, validate


def _signature(step: dict[str, Any]) -> str:
    return json.dumps(step, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A (zero denominator)"
    return f"{numerator / denominator:.4%} ({numerator}/{denominator})"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _safe_validation_categories(errors: list[str]) -> Counter[str]:
    """Collapse row-scoped validator messages without retaining case identifiers."""
    categories: Counter[str] = Counter()
    for error in errors:
        category = error.split(": ", 1)[1] if ": " in error else error
        categories[category] += 1
    return categories


def _operation_counts(gold: list[dict[str, Any]], predicted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gold_counts = Counter(step["operation"] for row in gold for step in json.loads(row["steps_json"]))
    pred_counts = Counter(step["operation"] for row in predicted for step in json.loads(row["steps_json"]))
    matched = gold_counts & pred_counts
    order = {name: rank for rank, (_, name, _) in enumerate(OPERATIONS)}
    names = sorted(gold_counts.keys() | pred_counts.keys(), key=lambda name: (order.get(name, len(order)), name))
    return [
        {
            "operation": name,
            "gold": gold_counts[name],
            "predicted": pred_counts[name],
            "matched": matched[name],
            "extra": max(0, pred_counts[name] - gold_counts[name]),
            "missing": max(0, gold_counts[name] - pred_counts[name]),
        }
        for name in names
    ]


def _retention_probe(gold: list[dict[str, Any]], predicted: list[dict[str, Any]]) -> dict[str, int]:
    """Score retention-named VERIFY_RECORD_PRESENT predictions without exposing IDs."""
    gold_by_id = {row["case_id"]: row for row in gold}
    predicted_count = exact_matches = 0
    for row in predicted:
        expected_row = gold_by_id.get(row["case_id"])
        if expected_row is None:
            continue
        expected_signatures = Counter(
            _signature(step) for step in json.loads(expected_row["steps_json"])
        )
        for step in json.loads(row["steps_json"]):
            locator = (step["system_id"] + " " + step["resource_id"]).casefold()
            if step["operation"] != "VERIFY_RECORD_PRESENT" or not any(
                word in locator for word in ("legal", "retention", "hold")
            ):
                continue
            predicted_count += 1
            signature = _signature(step)
            if expected_signatures[signature] > 0:
                exact_matches += 1
                expected_signatures[signature] -= 1
    return {"predicted": predicted_count, "exact_matches": exact_matches}


def _retention_evidence_probe(
    predicted: list[dict[str, Any]], dataset: Path
) -> dict[str, Any]:
    """Inspect only cited participant evidence; return aggregate marker counts."""
    files = {row["file_id"]: row for row in read_csv(dataset / "evidence_files.csv")[1]}
    activities = {row["activity_id"]: row for row in read_csv(dataset / "system_activity.csv")[1]}
    audits = {row["audit_id"]: row for row in read_csv(dataset / "user_audit_log.csv")[1]}
    candidates = incomplete = complete = incomplete_without_finding = 0
    pdf_count = pdf_pages = pdf_chars = active_hold_pdf_count = 0
    keywords = Counter({word: 0 for word in ("legal", "hold", "retention", "active", "present", "expires")})
    active_hold_pattern = re.compile(
        r"(?:legal[ _-]*hold.{0,50}\bactive\b|\bactive\b.{0,50}legal[ _-]*hold|"
        r"hold[ _-]*(?:status|state)\s*[:=]\s*active|status\s*[:=]\s*active.{0,50}hold)",
        re.I,
    )

    def source_text(evidence_id: str) -> tuple[str, str, int]:
        if evidence_id in files:
            path = dataset / files[evidence_id]["file_path"]
            if path.suffix.casefold() == ".pdf":
                try:
                    import fitz

                    with fitz.open(path) as document:
                        return " ".join(page.get_text() for page in document), "pdf", len(document)
                except Exception:
                    return "", "pdf-unreadable", 0
            try:
                return path.read_text(encoding="utf-8", errors="ignore"), path.suffix.casefold() or "file", 0
            except OSError:
                return "", "file-unreadable", 0
        if evidence_id in activities:
            return " ".join(activities[evidence_id].values()), "activity-row", 0
        if evidence_id in audits:
            return " ".join(audits[evidence_id].values()), "audit-row", 0
        return "", "unknown", 0

    for row in predicted:
        steps = json.loads(row["steps_json"])
        for step in steps:
            locator = (step["system_id"] + " " + step["resource_id"]).casefold()
            if step["operation"] != "VERIFY_RECORD_PRESENT" or not any(
                word in locator for word in ("legal", "retention", "hold")
            ):
                continue
            candidates += 1
            same_record_findings = [
                finding
                for finding in steps
                if finding["phase"] == "FINDING"
                and finding["system_id"] == step["system_id"]
                and finding["resource_id"] == step["resource_id"]
            ]
            refs = [step["evidence_id"]] if step["evidence_id"] else []
            refs.extend(finding["evidence_id"] for finding in same_record_findings if finding["evidence_id"])
            if row["deletion_status"] == "INCOMPLETE":
                incomplete += 1
                if not same_record_findings:
                    incomplete_without_finding += 1
            elif row["deletion_status"] == "COMPLETE":
                complete += 1
            for evidence_id in dict.fromkeys(refs):
                text, kind, page_count = source_text(evidence_id)
                if kind == "pdf":
                    pdf_count += 1
                    pdf_pages += page_count
                    pdf_chars += len(text)
                    active_hold_pdf_count += bool(active_hold_pattern.search(text))
                    for word in keywords:
                        keywords[word] += len(re.findall(rf"\b{re.escape(word)}\b", text, re.I))

    return {
        "candidates": candidates,
        "incomplete": incomplete,
        "incomplete_without_same_resource_finding": incomplete_without_finding,
        "complete": complete,
        "cited_pdfs": pdf_count,
        "cited_pdf_pages": pdf_pages,
        "cited_pdf_extracted_characters": pdf_chars,
        "cited_pdfs_with_explicit_active_hold_marker": active_hold_pdf_count,
        "cited_pdf_keyword_counts": dict(keywords),
    }


def score_rows(gold: list[dict[str, Any]], predicted: list[dict[str, Any]]) -> dict[str, Any]:
    """Reproduce the repository evaluator's metrics and add aggregate diagnostics."""
    pred_by_id = {row["case_id"]: row for row in predicted}
    gold_by_id = {row["case_id"]: row for row in gold}
    selected_ids = sorted(gold_by_id.keys() & pred_by_id.keys())
    step_tp = pred_steps = gold_steps = positional_total = 0
    field_matches = Counter({field: 0 for field in sorted(STEP_FIELDS)})
    field_total = Counter({field: 0 for field in sorted(STEP_FIELDS)})
    status_correct = sequence_correct = case_mismatches = 0
    pattern_counts: Counter[str] = Counter()

    for case_id in selected_ids:
        gold_row = gold_by_id[case_id]
        pred_row = pred_by_id[case_id]
        expected = json.loads(gold_row["steps_json"])
        actual = json.loads(pred_row["steps_json"])
        status_correct += gold_row["deletion_status"] == pred_row["deletion_status"]
        sequence_correct += expected == actual

        expected_steps = Counter(_signature(step) for step in expected)
        actual_steps = Counter(_signature(step) for step in actual)
        step_tp += sum((expected_steps & actual_steps).values())
        gold_steps += len(expected)
        pred_steps += len(actual)

        if gold_row["deletion_status"] != pred_row["deletion_status"]:
            pattern_counts[
                f"status: {gold_row['deletion_status']} -> {pred_row['deletion_status']}"
            ] += 1

        max_len = max(len(expected), len(actual))
        positional_total += max_len * len(STEP_FIELDS)
        for index in range(max_len):
            if index >= len(expected):
                pattern_counts[f"extra step: {actual[index]['operation']}"] += 1
                continue
            if index >= len(actual):
                pattern_counts[f"missing step: {expected[index]['operation']}"] += 1
                continue
            left, right = expected[index], actual[index]
            mismatched = []
            for field in sorted(STEP_FIELDS):
                field_total[field] += 1
                if left[field] == right[field]:
                    field_matches[field] += 1
                else:
                    mismatched.append(field)
            if mismatched:
                label = "positional field mismatch: " + ", ".join(mismatched)
                if left["operation"] != right["operation"]:
                    label += f"; operation {left['operation']} -> {right['operation']}"
                pattern_counts[label] += 1

        case_mismatches += (
            gold_row["deletion_status"] != pred_row["deletion_status"] or expected != actual
        )

    fields = []
    for field in sorted(STEP_FIELDS):
        denominator = positional_total
        fields.append(
            {
                "field": field,
                "matches": field_matches[field],
                "mismatches": denominator - field_matches[field],
                "denominator": denominator,
                "accuracy": _ratio(field_matches[field], denominator),
            }
        )

    return {
        "selected_cases": len(selected_ids),
        "status_correct": status_correct,
        "status_accuracy": _ratio(status_correct, len(selected_ids)),
        "sequence_correct": sequence_correct,
        "sequence_accuracy": _ratio(sequence_correct, len(selected_ids)),
        "case_mismatches": case_mismatches,
        "step_true_positive": step_tp,
        "predicted_steps": pred_steps,
        "gold_steps": gold_steps,
        "step_precision": _ratio(step_tp, pred_steps),
        "step_recall": _ratio(step_tp, gold_steps),
        "field_matches": sum(field_matches.values()),
        "field_total": positional_total,
        "field_accuracy": _ratio(sum(field_matches.values()), positional_total),
        "fields": fields,
        "operations": _operation_counts(gold, predicted),
        "top_patterns": sorted(pattern_counts.items(), key=lambda item: (-item[1], item[0]))[:10],
        "retention_probe": _retention_probe(gold, predicted),
    }


def render_report(
    *,
    prediction_path: Path,
    report_started: datetime,
    before_mtime: datetime,
    before_hash: str,
    after_mtime: datetime,
    after_hash: str,
    prediction_rows: int,
    distinct_prediction_ids: int,
    matched_sample_rows: int,
    sample_rows: int,
    validation_categories: Counter[str],
    metrics: dict[str, Any] | None,
) -> str:
    stable = before_mtime == after_mtime and before_hash == after_hash
    predates = before_mtime < report_started
    lines = [
        "# Agent 5 sample evaluation diagnostics",
        "",
        "This report evaluates an already-generated public-sample prediction CSV. It runs no inference and contains no per-case identifiers.",
        "",
        f"- Prediction file: `{prediction_path}`",
        f"- SHA-256 before/after evaluation: `{before_hash}` / `{after_hash}`",
        f"- Last modified before evaluation (UTC): `{before_mtime.isoformat(timespec='milliseconds')}`",
        f"- Evaluation started (UTC): `{report_started.isoformat(timespec='milliseconds')}`",
        f"- Prediction pre-existed evaluation: **{'yes' if predates else 'no'}**",
        f"- Prediction file unchanged during evaluation: **{'yes' if stable else 'no'}**",
        f"- Coverage: **{matched_sample_rows}/{sample_rows}** public requests ({_ratio(matched_sample_rows, sample_rows)})",
        f"- Prediction rows: {prediction_rows}; distinct case IDs: {distinct_prediction_ids}",
        "- Coverage is resolved-row coverage and is selection-biased; it is not full-sample or hidden-target accuracy.",
        "",
        "## Output validation",
        "",
    ]
    if validation_categories:
        lines.append("Validation failed. Error counts are grouped without case identifiers:")
        lines.extend(f"- {count}: {category}" for category, count in sorted(validation_categories.items()))
    else:
        lines.append("PASS: official structural and evidence-time contract checks passed for the supplied subset.")
    if metrics is None:
        lines.extend(["", "Scoring was skipped because prediction validation failed."])
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "",
            "## Recomputed metrics",
            "",
            f"- Status accuracy: {metrics['status_accuracy']}",
            f"- Exact-step precision: {metrics['step_precision']}",
            f"- Exact-step recall: {metrics['step_recall']}",
            f"- Positional-field accuracy: {metrics['field_accuracy']}",
            f"- Exact ordered-sequence accuracy: {metrics['sequence_accuracy']}",
            f"- Cases with any status or sequence mismatch: {metrics['case_mismatches']}/{metrics['selected_cases']}",
            f"- Exact step matches: {metrics['step_true_positive']}; predicted steps: {metrics['predicted_steps']}; reference steps: {metrics['gold_steps']}",
            "",
            "## Positional mismatch breakdown by field",
            "",
            "A missing or extra step counts as a mismatch in all seven fields, matching the repository evaluator.",
            "",
            "| Field | Matches | Mismatches | Compared positions | Accuracy |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for item in metrics["fields"]:
        lines.append(
            f"| {item['field']} | {item['matches']} | {item['mismatches']} | {item['denominator']} | {item['accuracy']} |"
        )
    lines.extend(
        [
            "",
            "## Operation mismatch breakdown",
            "",
            "Operation counts ignore the other six step fields and treat duplicate occurrences as a multiset.",
            "",
            "| Operation | Reference | Predicted | Matched | Extra | Missing |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in metrics["operations"]:
        lines.append(
            f"| {item['operation']} | {item['gold']} | {item['predicted']} | {item['matched']} | {item['extra']} | {item['missing']} |"
        )
    lines.extend(["", "## Most repeated generalized error patterns", ""])
    if metrics["top_patterns"]:
        lines.extend(f"- {count}: {pattern}" for pattern, count in metrics["top_patterns"])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Retention-related present-check probe",
            "",
            "This evaluation-only keyword filter counts predicted `VERIFY_RECORD_PRESENT` steps whose system or resource label mentions legal, retention, or hold. It is a diagnostic filter, not runtime logic.",
            f"- Predicted candidates: {metrics['retention_probe']['predicted']}",
            f"- Exact full-step matches to the public sample answers: {metrics['retention_probe']['exact_matches']}/{metrics['retention_probe']['predicted']}",
            f"- Incomplete candidates without a same-system/resource finding: {metrics['retention_evidence']['incomplete_without_same_resource_finding']}/{metrics['retention_evidence']['incomplete']}",
            f"- Complete candidates citing PDFs: {metrics['retention_evidence']['cited_pdfs']}; extracted pages/characters: {metrics['retention_evidence']['cited_pdf_pages']}/{metrics['retention_evidence']['cited_pdf_extracted_characters']}",
            f"- Cited PDFs with an explicit active-hold marker: {metrics['retention_evidence']['cited_pdfs_with_explicit_active_hold_marker']}/{metrics['retention_evidence']['cited_pdfs']}",
            f"- Cited-PDF keyword hits (legal/hold/retention/active/present/expires): {', '.join(f'{word}={count}' for word, count in metrics['retention_evidence']['cited_pdf_keyword_counts'].items())}",
            "These marker counts are a narrow evidence check; zero hits are a reason to keep the hold unresolved, not proof that no hold exists.",
            "",
            "## Scope and interpretation",
            "",
            "The prediction file contains only cases the current agent resolved. Its metrics therefore describe a selected subset, not an unbiased estimate of all 32 public cases or any hidden target cases. Answer labels were opened only after the supplied prediction rows passed validation and were used only for aggregate evaluator calculations. No missing prediction rows were generated or guessed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    before_mtime = _utc_mtime(args.predictions)
    before_hash = _file_sha256(args.predictions)
    header, predicted = read_csv(args.predictions)
    all_requests = read_csv(args.dataset / "sample_deletion_requests.csv")[1]
    request_ids = {row["case_id"] for row in all_requests}
    prediction_ids = {row.get("case_id", "") for row in predicted}
    selected_requests = [row for row in all_requests if row["case_id"] in prediction_ids]

    errors: list[str] = []
    if header != FIELDS:
        errors.append("incorrect predictions header or column order")
    elif not predicted:
        errors.append("partial evaluation requires at least one prediction")
    else:
        errors.extend(validate(predicted, selected_requests, evidence_times(args.dataset)))
        if prediction_ids - request_ids:
            errors.append("partial predictions contain unknown case IDs")
    categories = _safe_validation_categories(errors)

    # Public answer labels are deliberately loaded only after prediction validation.
    metrics = None
    if not errors:
        retention_evidence = _retention_evidence_probe(predicted, args.dataset)
        all_gold = read_csv(args.dataset / "sample_output.csv")[1]
        selected_ids = prediction_ids & request_ids
        selected_gold = [row for row in all_gold if row["case_id"] in selected_ids]
        metrics = score_rows(selected_gold, predicted)
        metrics["retention_evidence"] = retention_evidence

    after_mtime = _utc_mtime(args.predictions)
    after_hash = _file_sha256(args.predictions)
    report = render_report(
        prediction_path=args.predictions.resolve(),
        report_started=started,
        before_mtime=before_mtime,
        before_hash=before_hash,
        after_mtime=after_mtime,
        after_hash=after_hash,
        prediction_rows=len(predicted),
        distinct_prediction_ids=len(prediction_ids),
        matched_sample_rows=len(selected_requests),
        sample_rows=len(all_requests),
        validation_categories=categories,
        metrics=metrics,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8", newline="\n")
    print(report, end="")
    return 0 if not errors and before_hash == after_hash and before_mtime == after_mtime else 1


if __name__ == "__main__":
    raise SystemExit(main())
