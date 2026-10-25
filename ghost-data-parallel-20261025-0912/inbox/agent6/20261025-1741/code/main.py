"""Run the evidence-grounded deletion audit agent."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "code" / "tools"))

from audit_agent.cache import CachedChatModel, JsonResponseCache, canonical_hash, load_or_extract
from audit_agent.data import read_csv
from audit_agent.engine import AuditBlocked, CandidateIndex, audit_case
from audit_agent.identity import IdentityResolver
from audit_agent.model import FoundryChatModel, ModelConfigurationError, RunBudgetExceeded, UsageLedger
from audit_agent.policy import load_policy
from contract import FIELDS, evidence_times, validate


ENGINE_VERSION = "audit-engine-v16"
DEFAULT_AUTHORIZED_CAP_USD = 30.0
LOCAL_CONFIG_KEYS = {
    "AZURE_FOUNDRY_ENDPOINT", "AZURE_OPENAI_ENDPOINT",
    "AZURE_FOUNDRY_DEPLOYMENT", "DEPLOYMENT_NAME",
    "AZURE_FOUNDRY_MODEL_NAME", "MODEL_NAME",
    "MAX_RUN_COST_USD", "MAX_MODEL_CALLS",
    "AZURE_FOUNDRY_HOURLY_USD_PER_ACCELERATOR",
    "AZURE_FOUNDRY_ACCELERATOR_COUNT", "AZURE_FOUNDRY_BILLING_START_UTC",
    "AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS",
}


def _load_local_configuration() -> None:
    """Load only non-secret, allowlisted settings from ignored local env files.

    API-key variables are deliberately excluded. Foundry inference uses an
    authenticated Azure CLI token unless a caller explicitly provides a
    FOUNDRY key in the process environment. Datalab likewise reads its key
    only from the process environment.
    """
    for path in (ROOT / ".env.local", ROOT / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            name = name.strip()
            if name not in LOCAL_CONFIG_KEYS or name in os.environ:
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            if value and not (value.startswith("<") and value.endswith(">")):
                os.environ[name] = value

    # Accept existing Azure OpenAI-compatible names without copying secrets.
    if not os.environ.get("AZURE_FOUNDRY_ENDPOINT") and os.environ.get("AZURE_OPENAI_ENDPOINT"):
        os.environ["AZURE_FOUNDRY_ENDPOINT"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    if not os.environ.get("AZURE_FOUNDRY_DEPLOYMENT") and os.environ.get("DEPLOYMENT_NAME"):
        os.environ["AZURE_FOUNDRY_DEPLOYMENT"] = os.environ["DEPLOYMENT_NAME"]
    if not os.environ.get("AZURE_FOUNDRY_MODEL_NAME") and os.environ.get("MODEL_NAME"):
        os.environ["AZURE_FOUNDRY_MODEL_NAME"] = os.environ["MODEL_NAME"]


def _source_fingerprint() -> str:
    digest = hashlib.sha256(ENGINE_VERSION.encode("ascii"))
    sources = [ROOT / "code" / "audit_agent", ROOT / "code" / "prompts"]
    for folder in sources:
        for path in sorted(folder.rglob("*.py"), key=lambda item: str(item).casefold()):
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
        for path in sorted(folder.rglob("*.md"), key=lambda item: str(item).casefold()):
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    digest.update((ROOT / "code" / "main.py").read_bytes())
    return digest.hexdigest()


def _safe_case_name(case_id: str) -> str:
    return hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:20]


def _load_checkpoint(path: Path, run_key: str, case_id: str) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if value.get("run_key") != run_key or value.get("case_id") != case_id:
        return None
    row = value.get("row")
    if not isinstance(row, dict) or row.get("case_id") != case_id:
        return None
    return row


def _save_checkpoint(path: Path, run_key: str, row: dict[str, str], error: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({
        "run_key": run_key,
        "case_id": row["case_id"],
        "row": row,
        "error": error[:300],
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temporary.replace(path)


def _steps_json(steps: list[dict[str, object]]) -> str:
    return json.dumps(steps, ensure_ascii=False, separators=(",", ":"))


def _write_predictions(path: Path, rows: list[dict[str, str]], requests: list[dict[str, str]], dataset: Path) -> None:
    ordered = sorted(rows, key=lambda row: row["case_id"])
    errors = validate(ordered, requests, evidence_times(dataset))
    if errors:
        raise ValueError("Generated predictions failed structural validation:\n" + "\n".join(errors[:30]))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)
    temporary.replace(path)


def _usage_summary(
    model: FoundryChatModel,
    cache: JsonResponseCache,
    request_count: int,
    elapsed: float,
    datalab_usage: dict[str, object],
) -> dict[str, object]:
    actual = list(model.ledger.records)
    cached_records: list[dict[str, object]] = []
    for cache_entry in cache.reused_usage.values():
        for record in cache_entry.get("records", []):
            if isinstance(record, dict):
                cached_records.append(record)
    unique_cached = {canonical_hash(record): record for record in cached_records}
    all_calls = actual + list(unique_cached.values())
    successful = [row for row in all_calls if row.get("success")]
    usage_complete = bool(successful) and all(
        row.get(field) is not None
        for row in successful
        for field in ("input_tokens", "output_tokens", "total_tokens")
    )
    tokens_in = sum(int(row["input_tokens"]) for row in successful if row.get("input_tokens") is not None)
    tokens_out = sum(int(row["output_tokens"]) for row in successful if row.get("output_tokens") is not None)
    tokens_total = sum(int(row["total_tokens"]) for row in successful if row.get("total_tokens") is not None)
    target_api_calls = [row for row in all_calls if row.get("request_sent")]
    totals = {
        "api_call_attempts": len(target_api_calls),
        "successful_api_attempts": sum(bool(row.get("success")) for row in target_api_calls),
        "failed_api_attempts": sum(not bool(row.get("success")) for row in target_api_calls),
        "retries": sum(max(0, int(row.get("attempt", 1)) - 1) for row in all_calls),
        "input_tokens": tokens_in if usage_complete else None,
        "output_tokens": tokens_out if usage_complete else None,
        "total_tokens": tokens_total if usage_complete else None,
        "usage_unavailable_attempts": sum(any(row.get(field) is None for field in ("input_tokens", "output_tokens", "total_tokens")) for row in successful),
        "cache_hits": cache.hits,
        "cache_misses": cache.misses,
        "requests": request_count,
        "average_tokens_per_request": round(tokens_total / request_count, 2) if request_count and usage_complete else None,
        "provider": model.provider,
        "model": model.model,
        "deployment": model.deployment,
        "estimated_compute_cost_usd": max(
            (float(row["estimated_total_compute_cost_usd"]) for row in all_calls if row.get("estimated_total_compute_cost_usd") is not None),
            default=None,
        ),
        "authorized_cap_usd": model.cap,
        "uncapped_gpu_hours_authorized": model.uncapped_gpu_hours,
        "accelerator_equivalent_hours_since_run_start": round(model._gpu_hours(), 6),
        "gpu_hours_since_billing_start": round(model._gpu_hours(), 6) if model.billing_started else None,
        "elapsed_seconds": round(elapsed, 3),
        "usage_records": all_calls,
        "document_extraction": datalab_usage,
    }
    return totals


def run(args: argparse.Namespace) -> int:
    _load_local_configuration()
    if args.allow_uncapped_gpu_hours:
        os.environ["AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS"] = "1"
    started = time.monotonic()
    dataset = args.dataset.resolve()
    requests_path = (dataset / args.requests).resolve()
    requests = read_csv(requests_path)
    identities = read_csv(dataset / "user_identities.csv")
    audit_rows = read_csv(dataset / "user_audit_log.csv")
    rules = load_policy(read_csv(dataset / "deletion_rules.csv"))

    cache_root = args.cache_dir.resolve()
    observations, activity, extraction_cache_hit, data_hash, datalab_usage = load_or_extract(dataset, cache_root)
    print(f"extraction: observations={len(observations)} activity={len(activity)} cache_hit={str(extraction_cache_hit).lower()}")
    if args.extract_only:
        print(f"extraction fingerprint: {data_hash}")
        print(
            "Datalab extraction: "
            f"attempts={datalab_usage.get('request_attempts', 0)} "
            f"successes={datalab_usage.get('successful_requests', 0)} "
            f"failures={datalab_usage.get('failed_requests', 0)}"
        )
        return 0

    ledger = UsageLedger.create()
    try:
        if args.max_model_calls < 0:
            raise ModelConfigurationError("--max-model-calls must be zero (unlimited) or a positive integer")
        os.environ.setdefault("MAX_RUN_COST_USD", str(DEFAULT_AUTHORIZED_CAP_USD))
        model = FoundryChatModel(ledger, max_calls=args.max_model_calls)
    except (ModelConfigurationError, ValueError) as exc:
        print(f"inference unavailable: {exc}", file=sys.stderr)
        return 2

    prompt_root = ROOT / "code" / "prompts"
    intent_prompt = (prompt_root / "intent_classification.md").read_text(encoding="utf-8")
    evidence_prompt = (prompt_root / "evidence_classification.md").read_text(encoding="utf-8")
    policy_condition_prompt = (prompt_root / "policy_condition_resolution.md").read_text(encoding="utf-8")
    prompt_hash = canonical_hash({
        "intent": intent_prompt,
        "evidence": evidence_prompt,
        "policy_condition_resolution": policy_condition_prompt,
    })
    run_key = canonical_hash({
        "dataset": data_hash,
        "source": _source_fingerprint(),
        "engine": ENGINE_VERSION,
        "provider": model.provider,
        "model": model.model,
        "deployment": model.deployment,
        "prompts": prompt_hash,
        "schema_version": "structured-classification-v2",
    })
    run_dir = args.run_dir.resolve() / run_key
    checkpoint_dir = run_dir / "checkpoints"
    response_cache = JsonResponseCache(cache_root / "responses" / run_key)
    cached_model = CachedChatModel(model, response_cache, cache_only=args.cache_only)

    from audit_agent.model import classify_intents, ModelCallError

    try:
        intents = classify_intents(cached_model, requests, intent_prompt, batch_size=20)
    except (ModelCallError, RunBudgetExceeded) as exc:
        print(f"model run stopped before case processing: {type(exc).__name__}", file=sys.stderr)
        return 3
    intent_file = checkpoint_dir / "intents.json"
    intent_file.parent.mkdir(parents=True, exist_ok=True)
    intent_file.write_text(json.dumps({"run_key": run_key, "intents": intents}, ensure_ascii=False), encoding="utf-8")

    resolver = IdentityResolver(identities, audit_rows)
    candidate_index = CandidateIndex(observations, activity)
    results: list[dict[str, str]] = []
    unresolved: list[tuple[str, str]] = []
    for index, request in enumerate(requests, start=1):
        case_id = request["case_id"]
        checkpoint = checkpoint_dir / f"case-{_safe_case_name(case_id)}.json"
        checkpoint_exists = _load_checkpoint(checkpoint, run_key, case_id) is not None
        try:
            result = audit_case(
                request, intents[case_id], resolver, observations, activity,
                rules, cached_model, evidence_prompt, candidate_index,
                policy_condition_prompt=policy_condition_prompt,
            )
            row = {"case_id": case_id, "deletion_status": result.deletion_status, "steps_json": _steps_json(result.steps)}
            _save_checkpoint(checkpoint, run_key, row)
            results.append(row)
            suffix = " (resume; provider responses cached)" if checkpoint_exists else ""
            print(f"case {index}/{len(requests)} {case_id}: {result.deletion_status}{suffix}")
        except AuditBlocked as exc:
            unresolved.append((case_id, str(exc)))
            print(f"case {index}/{len(requests)} {case_id}: unresolved", file=sys.stderr)
        except RunBudgetExceeded as exc:
            print(f"model run stopped at case {case_id}: RunBudgetExceeded", file=sys.stderr)
            unresolved.append((case_id, str(exc)))
            break
        except ModelCallError as exc:
            print(f"model run stopped at case {case_id}: ModelCallError", file=sys.stderr)
            unresolved.append((case_id, str(exc)))
            break
        except Exception as exc:
            unresolved.append((case_id, f"{type(exc).__name__}: structured processing failure"))
            print(f"case {index}/{len(requests)} {case_id}: processing failure ({type(exc).__name__})", file=sys.stderr)

        if index % 10 == 0 or index == len(requests):
            usage = _usage_summary(model, response_cache, len(requests), time.monotonic() - started, datalab_usage)
            (run_dir / "usage_checkpoint.json").write_text(json.dumps(usage, ensure_ascii=False), encoding="utf-8")

    usage = _usage_summary(model, response_cache, len(requests), time.monotonic() - started, datalab_usage)
    (run_dir / "usage_checkpoint.json").write_text(json.dumps(usage, ensure_ascii=False), encoding="utf-8")
    if unresolved:
        unresolved_path = run_dir / "unresolved_cases.txt"
        unresolved_path.parent.mkdir(parents=True, exist_ok=True)
        unresolved_path.write_text("\n".join(f"{case_id}: {reason}" for case_id, reason in unresolved) + "\n", encoding="utf-8")
        print(f"release blocked: {len(unresolved)} unresolved; no output CSV written", file=sys.stderr)
        return 4
    if len(results) != len(requests):
        print("release blocked: request coverage is incomplete; no output CSV written", file=sys.stderr)
        return 4

    output_path = args.output.resolve()
    _write_predictions(output_path, results, requests, dataset)
    usage = _usage_summary(model, response_cache, len(requests), time.monotonic() - started, datalab_usage)
    usage["run_key"] = run_key
    usage["dataset_fingerprint"] = data_hash
    usage["output_sha256"] = hashlib.sha256(output_path.read_bytes()).hexdigest()
    usage["completed_at"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "usage_report.json").write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"validated output: {output_path} ({len(results)} rows)")
    cost = usage["estimated_compute_cost_usd"]
    cost_label = f"${cost:.6f}" if cost is not None else "unavailable (Foundry hourly rate not configured)"
    print(f"usage: calls={usage['api_call_attempts']} tokens={usage['total_tokens']} estimated_compute_cost_usd={cost_label}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "dataset")
    parser.add_argument("--requests", default="deletion_requests.csv", help="request CSV path relative to the dataset")
    parser.add_argument("--output", type=Path, default=ROOT / "output.csv")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".cache" / "audit_agent")
    parser.add_argument("--run-dir", type=Path, default=ROOT / ".run" / "audit_agent")
    parser.add_argument(
        "--cache-only", action="store_true",
        help="reuse cached model responses only; fail closed on a cache miss without calling the provider",
    )
    parser.add_argument(
        "--max-model-calls", type=int, default=0,
        help="maximum provider calls; 0 disables the call-count cap (default: 0)",
    )
    parser.add_argument("--extract-only", action="store_true", help="extract and cache evidence without calling a model")
    parser.add_argument(
        "--allow-uncapped-gpu-hours", action="store_true",
        help="allow uncapped Foundry managed-compute GPU hours; use only with explicit owner authorization",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
