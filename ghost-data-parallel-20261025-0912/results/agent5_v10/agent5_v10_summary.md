# Agent 5 v10 checkpoint evaluation

## Run state

At inspection, no v10 prediction process remained active. The final `.run/sample_v10/predictions.csv` was absent; the run had written `partial_predictions.csv` with 10 rows and 22 sample cases without a prediction. Evaluation used that checkpointed file only. No checkpoint row was promoted to final output. The prediction file SHA-256 remained `a08c2d825a5024540ac3958538bd1fecdf4da651278fbece53b5976d5e35c102` before and after evaluation.

## Results

- **Coverage:** 10/32 (31.25%); 22 cases have no prediction and are not scored as empty predictions.
- **Rows supplied:** 10/10 were scored; status accuracy 9/10 (90%). Predicted statuses: 4 COMPLETE and 6 INCOMPLETE; reference statuses for those rows: 5 COMPLETE and 5 INCOMPLETE.
- **Exact full-step multiset:** precision 22/47 (46.81%); recall 22/62 (35.48%).
- **Operations only:** precision 45/47 (95.74%); recall 45/62 (72.58%). Verification deficits total 17 steps: 9 VERIFY_RECORD_ABSENT, 5 VERIFY_RECORD_ANONYMIZED, and 3 VERIFY_RECORD_PRESENT. Extra operation counts: one REDACT_RECORD and one REPORT_EXPOSED_PII.
- **Positional fields:** 242/434 (55.76%), with missing/extra steps charged as seven field errors. The weakest fields were system_id and resource_id (24/62 each).
- **Order:** exact ordered sequence 0/10. All 10 checkpointed cases have a sequence mismatch; case_28 also has a status mismatch.
- **Full-sample accuracy:** unavailable because 22 rows are missing. These are public-sample metrics, not hidden-target performance.

## Contract checks

The official `evaluate.py --partial` completed successfully and validates the supplied rows against their matching requests and evidence-time bounds. `validate_output.py` passed for the 10 rows using a matching 10-request sidecar. Its full-request invocation rejected the partial file because case coverage is incomplete; this is not a row-level structural failure. The detailed report contains the per-operation counts and case-level mismatch notes.

## Artifacts

- `official_partial_evaluation.md` — official partial evaluator output.
- `v10_detailed_evaluation.md` — aggregate metrics, operation and field breakdowns, missing-case list, and per-case mismatches.
- `contract_validation_subset.md` — official contract check for supplied rows.
- `subset_sample_requests.csv` — minimal request sidecar used for that subset check.
- `evaluate_v10_checkpoint.py` — reproducible detailed comparison script.
- `official_partial_evaluation_stdout.txt` and `contract_validation.txt` — command output.

All Agent 5 v10 artifacts are in this directory. The live source, run files, cache, and root reports were not modified.
