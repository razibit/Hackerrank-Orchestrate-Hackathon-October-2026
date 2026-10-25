# Agent 5 sample evaluation diagnostics

This report evaluates an already-generated public-sample prediction CSV. It runs no inference and contains no per-case identifiers.

- Prediction file: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.run\target_v9\sample_partial_predictions.csv`
- SHA-256 before/after evaluation: `1a026b60feb81e725078e388dda8a58de29672ed6726ffaf49ff06d12d0d0a50` / `1a026b60feb81e725078e388dda8a58de29672ed6726ffaf49ff06d12d0d0a50`
- Last modified before evaluation (UTC): `2026-10-25T08:49:58.066+00:00`
- Evaluation started (UTC): `2026-10-25T09:39:24.997+00:00`
- Prediction pre-existed evaluation: **yes**
- Prediction file unchanged during evaluation: **yes**
- Coverage: **14/32** public requests (43.7500% (14/32))
- Prediction rows: 14; distinct case IDs: 14
- Coverage is resolved-row coverage and is selection-biased; it is not full-sample or hidden-target accuracy.

## Output validation

PASS: official structural and evidence-time contract checks passed for the supplied subset.

## Recomputed metrics

- Status accuracy: 100.0000% (14/14)
- Exact-step precision: 52.2388% (35/67)
- Exact-step recall: 40.2299% (35/87)
- Positional-field accuracy: 58.7849% (358/609)
- Exact ordered-sequence accuracy: 0.0000% (0/14)
- Cases with any status or sequence mismatch: 14/14
- Exact step matches: 35; predicted steps: 67; reference steps: 87

## Positional mismatch breakdown by field

A missing or extra step counts as a mismatch in all seven fields, matching the repository evaluator.

| Field | Matches | Mismatches | Compared positions | Accuracy |
|---|---:|---:|---:|---:|
| evidence_id | 66 | 543 | 609 | 10.8374% (66/609) |
| operation | 44 | 565 | 609 | 7.2250% (44/609) |
| phase | 67 | 542 | 609 | 11.0016% (67/609) |
| resource_id | 35 | 574 | 609 | 5.7471% (35/609) |
| state | 44 | 565 | 609 | 7.2250% (44/609) |
| step_no | 67 | 542 | 609 | 11.0016% (67/609) |
| system_id | 35 | 574 | 609 | 5.7471% (35/609) |

## Operation mismatch breakdown

Operation counts ignore the other six step fields and treat duplicate occurrences as a multiset.

| Operation | Reference | Predicted | Matched | Extra | Missing |
|---|---:|---:|---:|---:|---:|
| REPORT_REMAINING_RECORD | 9 | 9 | 9 | 0 | 0 |
| REPORT_EXPOSED_PII | 4 | 4 | 4 | 0 | 0 |
| REPORT_ACTIVE_DATA_FLOW | 3 | 3 | 3 | 0 | 0 |
| DISABLE_DATA_FLOW | 3 | 3 | 3 | 0 | 0 |
| DELETE_RECORD | 9 | 9 | 9 | 0 | 0 |
| REDACT_RECORD | 2 | 2 | 2 | 0 | 0 |
| ANONYMIZE_RECORD | 2 | 2 | 2 | 0 | 0 |
| VERIFY_RECORD_ABSENT | 23 | 10 | 10 | 0 | 13 |
| VERIFY_RECORD_PRESENT | 10 | 9 | 9 | 0 | 1 |
| VERIFY_RECORD_REDACTED | 5 | 5 | 5 | 0 | 0 |
| VERIFY_RECORD_ANONYMIZED | 8 | 2 | 2 | 0 | 6 |
| VERIFY_DATA_FLOW_DISABLED | 6 | 6 | 6 | 0 | 0 |
| VERIFY_RESTORE_BLOCKED | 3 | 3 | 3 | 0 | 0 |

## Most repeated generalized error patterns

- 9: positional field mismatch: resource_id, system_id
- 6: missing step: VERIFY_DATA_FLOW_DISABLED
- 6: positional field mismatch: operation, resource_id, state, system_id; operation VERIFY_RECORD_ABSENT -> VERIFY_RECORD_PRESENT
- 4: missing step: VERIFY_RECORD_ABSENT
- 4: missing step: VERIFY_RECORD_ANONYMIZED
- 4: positional field mismatch: operation, resource_id, state, system_id; operation VERIFY_RECORD_PRESENT -> VERIFY_RECORD_REDACTED
- 4: positional field mismatch: operation, resource_id, state, system_id; operation VERIFY_RECORD_REDACTED -> VERIFY_DATA_FLOW_DISABLED
- 3: missing step: VERIFY_RECORD_PRESENT
- 3: missing step: VERIFY_RESTORE_BLOCKED
- 3: positional field mismatch: operation, resource_id, state, system_id; operation VERIFY_RECORD_ANONYMIZED -> VERIFY_RESTORE_BLOCKED

## Retention-related present-check probe

This evaluation-only keyword filter counts predicted `VERIFY_RECORD_PRESENT` steps whose system or resource label mentions legal, retention, or hold. It is a diagnostic filter, not runtime logic.
- Predicted candidates: 3
- Exact full-step matches to the public sample answers: 0/3
- Incomplete candidates without a same-system/resource finding: 2/2
- Complete candidates citing PDFs: 1; extracted pages/characters: 2/1003
- Cited PDFs with an explicit active-hold marker: 0/1
- Cited-PDF keyword hits (legal/hold/retention/active/present/expires): legal=0, hold=0, retention=0, active=0, present=0, expires=0
These marker counts are a narrow evidence check; zero hits are a reason to keep the hold unresolved, not proof that no hold exists.

## Scope and interpretation

The prediction file contains only cases the current agent resolved. Its metrics therefore describe a selected subset, not an unbiased estimate of all 32 public cases or any hidden target cases. Answer labels were opened only after the supplied prediction rows passed validation and were used only for aggregate evaluator calculations. No missing prediction rows were generated or guessed.
