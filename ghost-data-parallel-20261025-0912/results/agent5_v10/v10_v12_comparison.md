# Independent v10 and v12 public-sample comparison

## Run and coverage

Both runs had exited when inspected, and neither had a final `predictions.csv`. Each had a 10-row `partial_predictions.csv`; neither was promoted to final output. Both cover the same 10 of 32 sample cases (31.25%), leaving 22 without prediction rows. Metrics below score only the supplied rows, so they are selection-biased.

The v10 and v12 prediction files are byte-identical. Their SHA-256 values match (`a08c2d825a5024540ac3958538bd1fecdf4da651278fbece53b5976d5e35c102`), and direct parsed-row comparison found no case, status, or step-array changes. Therefore, v12 has no per-case or step-level improvement or regression over v10 in these checkpoint files.

## Independently scored results

The official partial evaluator and Agent 5 detailed evaluator were run for each version, with the public sample labels read only within those evaluation steps. Both versions produced identical measurements:

| Measure | v10 | v12 |
|---|---:|---:|
| Coverage | 10/32 (31.25%) | 10/32 (31.25%) |
| Status accuracy on supplied rows | 9/10 (90%) | 9/10 (90%) |
| Exact full-step precision | 22/47 (46.81%) | 22/47 (46.81%) |
| Exact full-step recall | 22/62 (35.48%) | 22/62 (35.48%) |
| Positional field accuracy | 242/434 (55.76%) | 242/434 (55.76%) |
| Exact ordered sequence accuracy | 0/10 | 0/10 |
| Subset contract validation | PASS, 10 rows | PASS, 10 rows |

Operation-only precision was 45/47 (95.74%) and recall was 45/62 (72.58%) for both. The same 17 verification steps are absent from the predictions: 9 VERIFY_RECORD_ABSENT, 5 VERIFY_RECORD_ANONYMIZED, and 3 VERIFY_RECORD_PRESENT. The same extra operation counts occur in both: one REDACT_RECORD and one REPORT_EXPOSED_PII.

## Case-level reference mismatches (identical for both runs)

| Case | Gold status | Predicted status | Gold steps | Predicted steps | Exact full-step matches | Ordered sequence |
|---|---|---|---:|---:|---:|---|
| case_03 | COMPLETE | COMPLETE | 3 | 2 | 2 | mismatch |
| case_06 | INCOMPLETE | INCOMPLETE | 4 | 3 | 2 | mismatch |
| case_07 | INCOMPLETE | INCOMPLETE | 4 | 3 | 2 | mismatch |
| case_20 | INCOMPLETE | INCOMPLETE | 8 | 6 | 4 | mismatch |
| case_23 | INCOMPLETE | INCOMPLETE | 8 | 6 | 4 | mismatch |
| case_25 | COMPLETE | COMPLETE | 3 | 1 | 0 | mismatch |
| case_26 | COMPLETE | COMPLETE | 6 | 4 | 0 | mismatch |
| case_27 | COMPLETE | COMPLETE | 6 | 4 | 0 | mismatch |
| case_28 | COMPLETE | INCOMPLETE | 6 | 6 | 0 | mismatch |
| case_30 | INCOMPLETE | INCOMPLETE | 14 | 12 | 8 | mismatch |

The mismatch set is identical across v10 and v12: all 10 supplied cases have a sequence mismatch; case_28 also has the status mismatch. Their detailed operation deficits and positional field differences are recorded in [v10_detailed_evaluation.md](v10_detailed_evaluation.md) and [v12_detailed_evaluation.md](v12_detailed_evaluation.md). The same 22 missing case IDs are listed in both reports.

## Validation and limits

The official partial evaluator completed for both files. `validate_output.py` passed for each file against its matching 10-request subset and the evidence-time index. This validates only supplied rows; it does not establish complete 32-case coverage. No hidden-target accuracy is claimed.

The run files, caches, source, root reports, and root `output.csv` were not modified. All Agent 5 v10/v12 reports and comparison artifacts are under `results/agent5_v10/`.

## Supporting artifacts

- [v10 official partial evaluation](official_partial_evaluation.md)
- [v12 official partial evaluation](v12_official_partial_evaluation.md)
- [v10 detailed per-case report](v10_detailed_evaluation.md)
- [v12 detailed per-case report](v12_detailed_evaluation.md)
- [direct v10/v12 prediction-file comparison](v10_v12_prediction_diff.md)
- [v10 subset contract validation](contract_validation_subset.md)
- [v12 subset contract validation](v12_contract_validation_subset.md)
- [reproducible prediction comparator](compare_v10_v12_predictions.py)
