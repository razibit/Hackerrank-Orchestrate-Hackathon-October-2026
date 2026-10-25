# Agent 4 change summary

Candidate timestamp: 20261025-154511

## Changes

- Added local recursive JSON Schema validation for provider JSON: required fields, closed object keys, types, and enums. Malformed or schema-invalid provider output uses the existing three-attempt retry loop and then fails closed.
- All batch classifiers now correlate exact request/observation IDs without string coercion. Missing, duplicate, or mismatched IDs and provider truncation cause recursive batch splitting; a bad singleton remains a hard failure. No model output is coerced into an overall `COMPLETE` or `NOT_APPLICABLE` status.
- Added a deterministic legal-hold guard in `model.py`. A model cannot classify an observation as `LEGAL_HOLD_RECORD` without hold-specific evidence in that same observation. A present retention row and future `retention_until` alone yield category/condition `UNRESOLVED`. Explicit active or released status resolves to `TRUE` or `FALSE`; conflicting evidence remains `UNRESOLVED`.
- Revised all three prompts for original-language intent and negation/refusal, prompt-injection resistance, source-ID provenance, evidence-specific categories, content-grounded support retention, and unresolved missing facts. Evidence prompt revision 4 explicitly bars upgrading an unresolved retention row without hold-specific evidence.
- Corrected `UsageLedger.totals()` so each provider attempt after the first contributes one retry. Failed and retried attempts still contribute provider-reported token usage.
- Added deterministic mock tests for hold promotion, explicit/contradictory hold statuses, malformed output, schema failures, IDs, enums, truncation, retry accounting, prompt injection/intent guardrails, and cache invalidation.

## Versioning

Prompt text is hashed in the run/cache inputs; the source fingerprint includes the model module; and the response-cache key includes provider, model/deployment, prompt, payload, schema, and token limit. Prompt revisions change the key. The output schema is unchanged.

## Validation

Interpreter: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe`

Working directory: `D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent4`

Targeted command:

```powershell
$env:PYTHONPATH = 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent4\code'
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -p 'test_agent4_*.py' -v
```

Result: **18 tests passed** (`test-output-targeted.txt`).

Full-suite command:

```powershell
$env:PYTHONPATH = 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent4\code'
$env:GHOST_DATASET_PATH = 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\dataset'
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -v
```

Result: **88 tests passed** (`test-output-full.txt`). The suite reads only the policy CSV it needs from the read-only live dataset; no dataset file was copied or modified. The initial attempt without `GHOST_DATASET_PATH` failed because the isolated workspace intentionally omits `dataset/`; the supported-path rerun passed. Existing tests were not edited.

## Quality and tradeoffs

Agent 0's latest status reports a completed 518-request target pass with 294 blocked requests and no `output.csv` because unresolved cases remain. The v9 sample baseline remains 14/32 resolved, with exact-step precision 35/67 and recall 35/87 on the selected subset. This candidate has no measured CSV-quality delta: no model inference or sample/target evaluation was run. The active lease was not explicitly released. Prompt compliance tests and the synthetic parser regression do not establish live model accuracy.

The legal-hold guard can increase unresolved/blocked cases where hold evidence is missing or conflicting; this trades recall for avoiding unsupported retention claims. Batch splitting increases request count and latency for response-alignment/truncation failures: at most 39 calls for an intent batch of 20 and 9 for a batch of 5. Malformed/schema-invalid JSON still receives up to three client attempts. Prompt token impact was not measured.