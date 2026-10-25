# Evaluation report

## Scope and integrity

The agent reads only participant-facing files in dataset/ during prediction. The inference entry point does not read sample_output.csv. The sample evaluator reads sample_output.csv only after a prediction run. No organizer truth, generator internals, or case-family labels were used. Target predictions were not evaluated against hidden labels, and no hidden-set accuracy is claimed.

The agent fails closed when identity, physical scope, conditional policy, or current state cannot be established. It writes the official CSV only when all requests are resolved and validated. The final 518-request run therefore withheld output.csv: 262 cases resolved and 256 remained blocked. Writing a partial or guessed submission file would violate the contract.

## Preflight and automated regression suite

Preflight passed for 518 target requests, 32 sample requests, 15 policy rules, and 94 evidence manifest files. The manifest paths were checked, and the sample contract was validated.

Command:

    python -B -m unittest discover -s code/tests -v

Result: 65 tests passed. Coverage includes request negation, temporal aliases and alias reassignment, future evidence, partial snapshots, physical-scope separation, provenance, conditional policies, required retention, tombstones, active connectors, unsafe restoration, remediation ordering, output ordering and citation validation, malformed/truncated/omitted model output, cache-only replay with no provider calls, external-dataset preflight, uncapped-call configuration, source-grounded identifier precedence, and logical-system selection when a log has both a collector service and referenced system.

The target extraction cache holds 4,197 evidence observations and 4,011 activity observations. Evidence observations span SQL (891), logs (2,211), JSON (1,019), text (41), images (23), and PDFs (12), across 93 of 94 manifest files. The remaining manifest item is a schema-only SQL snapshot with snapshot_scope metadata and no resource rows; it is not used as proof of absence.

Fresh-package verification: the final archive was extracted into a new directory and its pinned requirements installed in a new Python 3.12.5 virtual environment. Preflight passed with the dataset supplied outside the archive, and all 65 tests passed. The packaged CLI replayed all 518 requests cache-only, reused 711 responses with zero misses and zero provider calls, resolved 262, blocked 256, and withheld output.csv as designed.

## Independent synthetic end-to-end cases

Three independently generated cases ran through the CLI and output validator. All three rows passed structural validation. No destructive action was performed.

| Case | Safety property | Observed result |
|---|---|---|
| custom-no-delete | Explicitly refuse deletion | NOT_APPLICABLE with no steps. |
| custom-old-alias-replica-flow | Resolve a unique historical alias; keep primary and replica scopes distinct; detect an active connector; order disabling before proposed replica removal | INCOMPLETE with seven ordered steps, grounded in the synthetic evidence. |
| custom-compliant-tombstone-retained-log | Preserve a required security record and verify a redacted tombstone | COMPLETE with two evidence-grounded verification steps. |

Executed command:

    python -B code/tools/build_synthetic_cases.py --dataset .run/custom_cases4/dataset
    python -B code/main.py --dataset .run/custom_cases4/dataset --output .run/custom_cases4/predictions.csv --cache-dir .run/custom_cases4/cache --run-dir .run/custom_cases4/runs --max-model-calls 0 --allow-uncapped-gpu-hours
    python -B code/tools/validate_output.py .run/custom_cases4/predictions.csv --dataset .run/custom_cases4/dataset

Measured result: 3/3 validated rows; the original run made 3 successful Foundry calls, with no failed call or retry; 5,227 input and 1,983 output tokens (7,210 total); 21.172 seconds of instrumented model-client time and 22.202 seconds observed CLI wall time. The final-source cache-only rerun made zero provider calls and the validator again printed PASS: 3 rows satisfy structural checks.

## Supplied public sample

The final sample inference replay reused 40 valid cached responses and made one additional policy-resolution call. After the final source-ID correction, the sample was replayed again with cache-only mode: all 41 responses were reused and no new provider calls were made. Both runs resolve 16 of 32 rows; the other 16 remain unresolved and were not serialized as predictions. Since the full prediction file is incomplete, a full 32-row official evaluation could not be run. A separate partial evaluator compared only the 16 resolved rows with public labels; the final-source metrics are unchanged.

| Metric on resolved subset | Result |
|---|---:|
| Prediction coverage | 16/32 |
| Status accuracy | 16/16 (100.0000%) |
| Exact step precision | 42/77 (54.5455%) |
| Exact step recall | 42/97 (43.2990%) |
| Positional field accuracy | 424/679 (62.4448%) |
| Exact ordered-sequence accuracy | 1/16 (6.2500%) |

This subset may be selection-biased and is not full-sample accuracy. Mismatched resolved cases were case_03, case_06, case_07, case_08, case_10, case_20, case_21, and case_23 through case_30. Step comparison includes all seven fields and exact order.

The 16 unresolved sample cases comprise three without subject-linked evidence, nine with unresolved SECURITY_AUDIT_LOG retention conditions, two BACKUP_ARCHIVE conditions, one ACCOUNT_TOMBSTONE condition, and one SUPPORT_MESSAGE condition. These rows remain blocked rather than being inferred from their labels.

## Full target run and failures

The final-source cache-only target replay processed all 518 requests. It resolved 262 and blocked 256. The primary blocker recorded for each unresolved case is 171 SECURITY_AUDIT_LOG retention conditions, 29 SUPPORT_MESSAGE conditions, 25 BACKUP_ARCHIVE conditions, two ACCOUNT_TOMBSTONE conditions, four cases without subject-linked evidence, four unclassified material evidence categories, and 21 other isolated evidence or consistency failures. These are first-stopping conditions, so one case may contain additional unresolved facts. Case 87 now uses the evidence's explicit `security_service` system instead of the log collector's `search_index_service`; it remains blocked by unresolved restore-control evidence for an active backup, and its candidate evidence also includes a security record with no supplied retention date. The dominant retention rule applies only within a supplied retention period, but the relevant dates or conditions are absent or cannot be grounded for those cases. Support, backup, tombstone, and isolated failures likewise lack sufficient source evidence or consistent scope/state. Repeating inference cannot supply facts that are not present in participant-visible evidence.

General changes made during evaluation:

- Placeholder values such as null, none, and n/a no longer count as conflicting stable subject references; actual conflicting identifiers still block.
- A second-pass policy-condition resolver can interpret support-message content only when direct source content/context fields are present. Missing content remains unresolved.
- The public evaluator supports an explicit partial mode and marks its selection bias.
- Source-grounded system and resource IDs override model mutations, and explicit logical system fields take priority over log collector `service` values even when the model response mutates the IDs.
- The suite now has 65 regression tests, including resolver, placeholder-reference, cache-only, external-dataset, and source-grounded-ID precedence cases.

No output.csv was written at the repository root because 256 cases remain unresolved. This is a release blocker. Do not interpret the resolved count as target accuracy; the target labels are unavailable to this evaluation.
