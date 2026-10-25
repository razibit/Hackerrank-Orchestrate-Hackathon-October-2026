# v15 checkpointed public-sample evaluation

## Scope and coverage

The v15 process exited without producing the final `predictions.csv`. This report scores only its existing checkpointed `partial_predictions.csv`; no checkpoint rows were promoted to a final output.
- Public sample size: 32 cases.
- Checkpointed predictions: 11/32 (34.38%).
- Missing prediction rows: 21 (not scored as empty predictions).
- Resolved-row evaluation denominator: 11 cases; these metrics are selection-biased.
- Prediction SHA-256: `12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565`.

## Status, exact steps, positions, and order

- Status accuracy on checkpointed rows: 90.91% (10/11).
- Exact full-step multiset precision: 50.85% (30/59).
- Exact full-step multiset recall: 39.47% (30/76).
- Positional field accuracy (all seven fields; absent/extra steps count as seven errors): 58.65% (312/532).
- Exact ordered sequence accuracy: 0.00% (0/11).
- Full 32-case accuracy is unavailable because 22 cases have no prediction row.

### Status counts on the scored rows

| Status | Gold | Prediction |
|---|---:|---:|
| COMPLETE | 5 | 4 |
| INCOMPLETE | 6 | 7 |

### Positional field breakdown

| Field | Correct | Compared | Accuracy |
|---|---:|---:|---:|
| evidence_id | 54 | 76 | 71.05% (54/76) |
| operation | 39 | 76 | 51.32% (39/76) |
| phase | 57 | 76 | 75.00% (57/76) |
| resource_id | 32 | 76 | 42.11% (32/76) |
| state | 39 | 76 | 51.32% (39/76) |
| step_no | 59 | 76 | 77.63% (59/76) |
| system_id | 32 | 76 | 42.11% (32/76) |

## Operation counts on the scored rows

- Operation-only multiset precision: 96.61% (57/59).
- Operation-only multiset recall: 75.00% (57/76).
| Operation | Gold | Prediction | Matched | Missing | Extra | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| ANONYMIZE_RECORD | 2 | 2 | 2 | 0 | 0 | 100.00% (2/2) | 100.00% (2/2) |
| DELETE_RECORD | 7 | 7 | 7 | 0 | 0 | 100.00% (7/7) | 100.00% (7/7) |
| DISABLE_DATA_FLOW | 3 | 3 | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |
| REDACT_RECORD | 2 | 3 | 2 | 0 | 1 | 66.67% (2/3) | 100.00% (2/2) |
| REPORT_ACTIVE_DATA_FLOW | 3 | 3 | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |
| REPORT_EXPOSED_PII | 4 | 5 | 4 | 0 | 1 | 80.00% (4/5) | 100.00% (4/4) |
| REPORT_REMAINING_RECORD | 7 | 7 | 7 | 0 | 0 | 100.00% (7/7) | 100.00% (7/7) |
| VERIFY_DATA_FLOW_DISABLED | 6 | 6 | 6 | 0 | 0 | 100.00% (6/6) | 100.00% (6/6) |
| VERIFY_RECORD_ABSENT | 18 | 8 | 8 | 10 | 0 | 100.00% (8/8) | 44.44% (8/18) |
| VERIFY_RECORD_ANONYMIZED | 7 | 2 | 2 | 5 | 0 | 100.00% (2/2) | 28.57% (2/7) |
| VERIFY_RECORD_PRESENT | 9 | 5 | 5 | 4 | 0 | 100.00% (5/5) | 55.56% (5/9) |
| VERIFY_RECORD_REDACTED | 5 | 5 | 5 | 0 | 0 | 100.00% (5/5) | 100.00% (5/5) |
| VERIFY_RESTORE_BLOCKED | 3 | 3 | 3 | 0 | 0 | 100.00% (3/3) | 100.00% (3/3) |

## Case-level comparison

| Case | Gold status | Predicted status | Gold steps | Predicted steps | Exact full-step matches | Exact sequence | Positional fields |
|---|---|---|---:|---:|---:|---|---:|
| case_03 | COMPLETE | COMPLETE | 3 | 2 | 2 | no | 66.67% (14/21) |
| case_06 | INCOMPLETE | INCOMPLETE | 4 | 3 | 2 | no | 67.86% (19/28) |
| case_07 | INCOMPLETE | INCOMPLETE | 4 | 3 | 2 | no | 67.86% (19/28) |
| case_18 | INCOMPLETE | INCOMPLETE | 14 | 12 | 8 | no | 71.43% (70/98) |
| case_20 | INCOMPLETE | INCOMPLETE | 8 | 6 | 4 | no | 64.29% (36/56) |
| case_23 | INCOMPLETE | INCOMPLETE | 8 | 6 | 4 | no | 67.86% (38/56) |
| case_25 | COMPLETE | COMPLETE | 3 | 1 | 0 | no | 14.29% (3/21) |
| case_26 | COMPLETE | COMPLETE | 6 | 4 | 0 | no | 28.57% (12/42) |
| case_27 | COMPLETE | INCOMPLETE | 6 | 6 | 0 | no | 45.24% (19/42) |
| case_28 | COMPLETE | COMPLETE | 6 | 4 | 0 | no | 28.57% (12/42) |
| case_30 | INCOMPLETE | INCOMPLETE | 14 | 12 | 8 | no | 71.43% (70/98) |

All predicted cases have some status or sequence mismatch: case_03, case_06, case_07, case_18, case_20, case_23, case_25, case_26, case_27, case_28, case_30.
Cases with no checkpointed prediction (not scored): case_01, case_02, case_04, case_05, case_08, case_09, case_10, case_11, case_12, case_13, case_14, case_15, case_16, case_17, case_19, case_21, case_22, case_24, case_29, case_31, case_32.

### Mismatch details

### case_03
- Status: gold `COMPLETE`; prediction `COMPLETE` (match).
- Step counts: gold 3, prediction 2; exact full-step matches 2; sequence differs.
- Gold-only operations: VERIFY_RECORD_ANONYMIZED x1.
- Prediction-only operations: none.
- Positional differences: step 3: missing prediction (VERIFY_RECORD_ANONYMIZED).
### case_06
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 4, prediction 3; exact full-step matches 2; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1.
- Prediction-only operations: none.
- Positional differences: step 3: resource_id, system_id; step 4: missing prediction (VERIFY_RECORD_ABSENT).
### case_07
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 4, prediction 3; exact full-step matches 2; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1.
- Prediction-only operations: none.
- Positional differences: step 3: resource_id, system_id; step 4: missing prediction (VERIFY_RECORD_ABSENT).
### case_18
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 14, prediction 12; exact full-step matches 8; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_PRESENT x1.
- Prediction-only operations: none.
- Positional differences: step 9: resource_id, system_id; step 10: operation, resource_id, state, system_id; step 11: operation, resource_id, state, system_id; step 12: operation, resource_id, state, system_id; step 13: missing prediction (VERIFY_RECORD_ANONYMIZED); step 14: missing prediction (VERIFY_DATA_FLOW_DISABLED).
### case_20
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 8, prediction 6; exact full-step matches 4; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_PRESENT x1.
- Prediction-only operations: none.
- Positional differences: step 5: resource_id, system_id; step 6: operation, resource_id, state, system_id; step 7: missing prediction (VERIFY_RECORD_PRESENT); step 8: missing prediction (VERIFY_DATA_FLOW_DISABLED).
### case_23
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 8, prediction 6; exact full-step matches 4; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_PRESENT x1.
- Prediction-only operations: none.
- Positional differences: step 5: resource_id, system_id; step 6: resource_id, system_id; step 7: missing prediction (VERIFY_RECORD_ABSENT); step 8: missing prediction (VERIFY_RECORD_PRESENT).
### case_25
- Status: gold `COMPLETE`; prediction `COMPLETE` (match).
- Step counts: gold 3, prediction 1; exact full-step matches 0; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_ANONYMIZED x1.
- Prediction-only operations: none.
- Positional differences: step 1: operation, resource_id, state, system_id; step 2: missing prediction (VERIFY_RECORD_PRESENT); step 3: missing prediction (VERIFY_RECORD_ANONYMIZED).
### case_26
- Status: gold `COMPLETE`; prediction `COMPLETE` (match).
- Step counts: gold 6, prediction 4; exact full-step matches 0; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_ANONYMIZED x1.
- Prediction-only operations: none.
- Positional differences: step 1: operation, resource_id, state, system_id; step 2: operation, resource_id, state, system_id; step 3: operation, resource_id, state, system_id; step 4: operation, resource_id, state, system_id; step 5: missing prediction (VERIFY_DATA_FLOW_DISABLED); step 6: missing prediction (VERIFY_RESTORE_BLOCKED).
### case_27
- Status: gold `COMPLETE`; prediction `INCOMPLETE` (mismatch).
- Step counts: gold 6, prediction 6; exact full-step matches 0; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_ANONYMIZED x1.
- Prediction-only operations: REDACT_RECORD x1, REPORT_EXPOSED_PII x1.
- Positional differences: step 1: operation, phase, resource_id, state, system_id; step 2: evidence_id, operation, phase, resource_id, state, system_id; step 3: evidence_id, operation, resource_id, state, system_id; step 4: evidence_id, operation, resource_id, state, system_id; step 5: evidence_id; step 6: evidence_id.
### case_28
- Status: gold `COMPLETE`; prediction `COMPLETE` (match).
- Step counts: gold 6, prediction 4; exact full-step matches 0; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_ANONYMIZED x1.
- Prediction-only operations: none.
- Positional differences: step 1: operation, resource_id, state, system_id; step 2: operation, resource_id, state, system_id; step 3: operation, resource_id, state, system_id; step 4: operation, resource_id, state, system_id; step 5: missing prediction (VERIFY_DATA_FLOW_DISABLED); step 6: missing prediction (VERIFY_RESTORE_BLOCKED).
### case_30
- Status: gold `INCOMPLETE`; prediction `INCOMPLETE` (match).
- Step counts: gold 14, prediction 12; exact full-step matches 8; sequence differs.
- Gold-only operations: VERIFY_RECORD_ABSENT x1, VERIFY_RECORD_PRESENT x1.
- Prediction-only operations: none.
- Positional differences: step 9: resource_id, system_id; step 10: operation, resource_id, state, system_id; step 11: operation, resource_id, state, system_id; step 12: operation, resource_id, state, system_id; step 13: missing prediction (VERIFY_RECORD_ANONYMIZED); step 14: missing prediction (VERIFY_DATA_FLOW_DISABLED).

## Contract validity

PASS: official contract validation succeeded for the checkpointed rows and their matching sample requests/evidence times.
The official `validate_output.py` full-request invocation rejects a partial file for coverage mismatch; a separate invocation against the matching 10-request subset passed. Neither result implies complete sample coverage.

## Limitations

Public sample only; no hidden-target accuracy claim. Checkpointed rows remain diagnostic and are not a finalized submission.
