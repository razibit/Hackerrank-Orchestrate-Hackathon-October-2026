# Agent 4 change summary

Candidate timestamp: 20261025-153720

## Changes

- Added local recursive JSON Schema checks for provider responses, including required fields, closed object keys, field types, and enums. Invalid JSON and schema-invalid responses continue through the existing three-attempt bounded retry loop; persistent failures fail closed.
- Batch classifiers now correlate exact case/observation IDs without string coercion. Missing, duplicate, or mismatched IDs and provider truncation cause bounded recursive batch splitting; a bad singleton still fails closed. No model result is converted to an overall `COMPLETE` or `NOT_APPLICABLE` status.
- Corrected `UsageLedger.totals()` retry accounting to count each attempt after the first once. Failed and retried attempts continue to contribute any provider-reported token usage.
- Revised all three prompts: original-language intent and negation/refusal, prompt-injection resistance, category definitions and source-ID provenance, explicit `UNRESOLVED` handling, content-grounded support retention, and a rule that a present retention row/future `retention_until` does not establish an active legal hold.
- Added deterministic mock tests for malformed/schema-invalid output, bounded retry accounting, truncation, missing/duplicate/mismatched IDs, invalid enums/types, cache versioning by prompt content, and prompt guardrails.
- Kept response versioning intact: prompt text is hashed in the run/cache inputs, the model source is included in the run fingerprint, and the response-cache key includes model/deployment, prompt, payload, schema, and token limit. Prompt revision text therefore produces new cache keys; the output schema itself is unchanged.

## Validation

Interpreter: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe`

Targeted command:

```powershell
$env:PYTHONPATH = 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent4\code'
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -p 'test_agent4_*.py' -v
```

Result: **16 tests passed** (`test-output-targeted.txt`).

Full-suite command:

```powershell
$env:PYTHONPATH = 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent4\code'
$env:GHOST_DATASET_PATH = 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\dataset'
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -v
```

Result: **86 tests passed** (`test-output-full.txt`). The suite reads the policy CSV from the live dataset; no dataset files were copied or modified. An initial full-suite attempt without `GHOST_DATASET_PATH` failed because this isolated workspace intentionally has no `dataset/`; the rerun with the supported environment variable passed. No existing test files were modified.

## Quality and tradeoffs

No model inference or sample/target evaluation was run because Agent 0 still owns the active Foundry lease. The v9 sample metrics remain Agent 0's reported baseline; this candidate has no measured CSV-quality delta. Prompt compliance tests are guardrail checks, not evidence that a live model follows the prompt. Recursive splitting can increase request count and latency for malformed batch alignment; for an intent batch of 20 the response-alignment path is bounded by a binary tree of at most 39 requests, while evidence and policy batches of 5 are bounded by 9. A malformed JSON/schema response still uses up to three attempts and then fails closed. Prompt token impact was not measured.

The existing engine owns final system/resource-ID grounding. The full suite's `test_source_grounded_ids_override_model_mutations` regression passed; this candidate changes prompts and response types but does not edit `engine.py`.

## Cross-owner proposal

See `legal-hold-engine-proposal.md`. It describes a narrow deterministic guard for Agent 0/Agent 3 review; no out-of-owner source file was changed.