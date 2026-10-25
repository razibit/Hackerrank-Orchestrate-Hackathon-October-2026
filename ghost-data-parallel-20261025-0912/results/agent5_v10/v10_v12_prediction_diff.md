# Direct v10 versus v12 prediction comparison

This comparison reads only the two prediction CSV files; sample labels are not loaded here. Public-sample scoring is documented in the separate detailed evaluation reports.

- v10 coverage: 10/32 (31.25%).
- v12 coverage: 10/32 (31.25%).
- Same case IDs: 10/10; v10-only: 0; v12-only: 0.
- Status changed for 0/10 common cases.
- Parsed step arrays changed for 0/10 common cases.
- Byte-identical prediction files: True.
- v10 SHA-256: `a08c2d825a5024540ac3958538bd1fecdf4da651278fbece53b5976d5e35c102`.
- v12 SHA-256: `a08c2d825a5024540ac3958538bd1fecdf4da651278fbece53b5976d5e35c102`.

| Case | Status | v10 steps | v12 steps | Parsed sequence | Field value deltas | Steps missing in v10 | Steps missing in v12 |
|---|---|---:|---:|---|---:|---:|---:|
| case_03 | same | 2 | 2 | same | 0 | 0 | 0 |
| case_06 | same | 3 | 3 | same | 0 | 0 | 0 |
| case_07 | same | 3 | 3 | same | 0 | 0 | 0 |
| case_20 | same | 6 | 6 | same | 0 | 0 | 0 |
| case_23 | same | 6 | 6 | same | 0 | 0 | 0 |
| case_25 | same | 1 | 1 | same | 0 | 0 | 0 |
| case_26 | same | 4 | 4 | same | 0 | 0 | 0 |
| case_27 | same | 4 | 4 | same | 0 | 0 | 0 |
| case_28 | same | 6 | 6 | same | 0 | 0 | 0 |
| case_30 | same | 12 | 12 | same | 0 | 0 | 0 |

## Cases present in only one run

- v10 only: none.
- v12 only: none.

## Changed cases

None. Every common case has the same status and parsed step sequence in v10 and v12.
