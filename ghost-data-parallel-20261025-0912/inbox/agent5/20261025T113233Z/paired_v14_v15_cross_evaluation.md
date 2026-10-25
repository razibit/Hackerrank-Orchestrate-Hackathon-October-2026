# Paired public-sample cross-evaluation: v14 vs v15

Both existing prediction files passed official schema and evidence-time validation before this script read `sample_output.csv`. No inference was run. Metrics below use only case IDs present in both files, so they are paired but still a selected subset.

- v14 coverage: 8/32; v15 coverage: 11/32.
- Common scored cases: 8/32.
- v14-only cases: 0; v15-only cases: 3.
- v14 file SHA-256: `d80b4d332a049ff8f60364b8fc593c139041939b44b0a1c787f6e731654a6848`.
- v15 file SHA-256: `12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565`.

| Metric on shared cases | v14 | v15 | v15 minus v14 |
|---|---:|---:|---:|
| Status accuracy | 87.50% (7/8) | 87.50% (7/8) | +0.00 pp |
| Exact-step precision | 41.03% (16/39) | 41.03% (16/39) | +0.00 pp |
| Exact-step recall | 31.37% (16/51) | 31.37% (16/51) | +0.00 pp |
| Positional fields | 53.78% (192/357) | 53.78% (192/357) | +0.00 pp |
| Exact ordered sequence | 0.00% (0/8) | 0.00% (0/8) | +0.00 pp |

Exact-step TP changes by case: improved 0, regressed 0, unchanged 8 of 8.

| Shared case | v14 status correct | v15 status correct | Gold steps | v14 predicted | v15 predicted | Exact-step TP v14 | Exact-step TP v15 | TP delta | Order v14 | Order v15 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| case_06 | yes | yes | 4 | 3 | 3 | 2 | 2 | +0 | no | no |
| case_07 | yes | yes | 4 | 3 | 3 | 2 | 2 | +0 | no | no |
| case_23 | yes | yes | 8 | 6 | 6 | 4 | 4 | +0 | no | no |
| case_25 | yes | yes | 3 | 1 | 1 | 0 | 0 | +0 | no | no |
| case_26 | no | yes | 6 | 6 | 4 | 0 | 0 | +0 | no | no |
| case_27 | yes | no | 6 | 4 | 6 | 0 | 0 | +0 | no | no |
| case_28 | yes | yes | 6 | 4 | 4 | 0 | 0 | +0 | no | no |
| case_30 | yes | yes | 14 | 12 | 12 | 8 | 8 | +0 | no | no |

## Operation differences on shared cases

| Operation | Gold | v14 | v15 | v14 missing | v15 missing | v14 extra | v15 extra |
|---|---:|---:|---:|---:|---:|---:|---:|
| ANONYMIZE_RECORD | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| DELETE_RECORD | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| DISABLE_DATA_FLOW | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| REDACT_RECORD | 1 | 2 | 2 | 0 | 0 | 1 | 1 |
| REPORT_ACTIVE_DATA_FLOW | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| REPORT_EXPOSED_PII | 2 | 3 | 3 | 0 | 0 | 1 | 1 |
| REPORT_REMAINING_RECORD | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| VERIFY_DATA_FLOW_DISABLED | 4 | 4 | 4 | 0 | 0 | 0 | 0 |
| VERIFY_RECORD_ABSENT | 13 | 5 | 5 | 8 | 8 | 0 | 0 |
| VERIFY_RECORD_ANONYMIZED | 5 | 1 | 1 | 4 | 4 | 0 | 0 |
| VERIFY_RECORD_PRESENT | 6 | 4 | 4 | 2 | 2 | 0 | 0 |
| VERIFY_RECORD_REDACTED | 4 | 4 | 4 | 0 | 0 | 0 | 0 |
| VERIFY_RESTORE_BLOCKED | 3 | 3 | 3 | 0 | 0 | 0 | 0 |

## Interpretation

This paired comparison distinguishes changes on the same cases from differences caused only by changing which cases resolved. It does not establish causal improvement or hidden-set performance. If few cases overlap, treat percentage-point deltas as weak evidence.
