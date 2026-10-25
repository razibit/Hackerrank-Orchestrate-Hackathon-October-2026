# Agent 1 extractor follow-up: stale assertion and v15 compatibility

## Decision

The one old assertion was stale. Its fixture contains a finance retention-register row and a future retain-until date, but no hold field or active-hold statement. The extractor intentionally maps that row to UNRESOLVED, PRESENT, snapshot. The model/category policy must not invent an active legal hold from a retention date.

I changed only that assertion in the isolated work copy: LEGAL_HOLD_RECORD to UNRESOLVED. No extractor code was changed.

The retention-specific extractor behavior is general and compatible with v15: it is based on the record schema and an explicit “retain until” row shape, preserves the source path and row fields, and does not use case IDs or resource-ID prefixes. The live v15 extractor and test already contain this behavior.

Do not replace the v15 extractor with the older full candidate from inbox/agent1/20261025-1534. That candidate still merges all non-empty fields across a trace into each sibling line (candidate lines 527 and 566). The v15 source now pairs only uniquely matched operation starts with readback completions, keeps state/result fields on their source lines, and carries only whitelisted identity context (v15 extractor lines 525–633). Replacing the newer file would regress its trace provenance safeguards. The v15 test is already updated and adds state/proof, record_type, and source_path assertions (v15 test lines 140–153). No integration is recommended from this follow-up.

## Test results

The isolated code import was verified to resolve to work/agent1/code/audit_agent/__init__.py. Tests used the root virtual-environment interpreter, with PYTHONPATH set to the isolated code directory. The full suite’s read-only dataset dependency was supplied through GHOST_DATASET_PATH; no dataset files were copied or modified.

- Before the assertion update, the extractor module ran 20 tests with exactly one failure: the stale LEGAL_HOLD_RECORD expectation. See baseline-test-extractors.txt.
- After the update, Agent 1 focused tests: 2 passed. See focused-agent1.txt.
- After the update, extractor module: 20 passed. See focused-extractors.txt.
- Full isolated suite without GHOST_DATASET_PATH: 72 tests, 30 FileNotFoundError setup errors because this workspace has no local dataset directory. This was a test-path setup failure, not a code assertion failure. See full-suite.txt.
- Full isolated suite with GHOST_DATASET_PATH set to the read-only participant dataset: 72 passed. See full-suite-readonly-dataset.txt.

No live inference was run, and no active target-run, output, or checkpoint files were accessed. Root source, reports, output, checkpoints, and code.zip were not changed; the v15 source and test were inspected read-only.