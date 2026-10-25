# Executed independent synthetic cases

These three cases were generated independently of the supplied challenge labels and passed through the CLI, Foundry model, audit engine, and structural output validator. They are functional checks, not challenge-label accuracy measurements. No real deletion was performed.

| Case | Input condition | Executed outcome |
|---|---|---|
| custom-no-delete | The person requests a copy and explicitly says not to delete the account or personal information. | NOT_APPLICABLE; steps_json is empty. |
| custom-old-alias-replica-flow | A historical alias identifies one subject; the primary snapshot is absent; an older replica retains a record; an active connector can sync data. | INCOMPLETE; seven ordered steps identify the replica and connector, propose disabling the connector before replica removal, and verify primary absence, replica absence, and disabled flow. Findings cite the synthetic evidence. |
| custom-compliant-tombstone-retained-log | A policy-required security record remains and the account tombstone is redacted. | COMPLETE; two grounded verification steps confirm the retained record and redacted tombstone. |

Executed commands:

    python -B code/tools/build_synthetic_cases.py --dataset .run/custom_cases4/dataset
    python -B code/main.py --dataset .run/custom_cases4/dataset --output .run/custom_cases4/predictions.csv --cache-dir .run/custom_cases4/cache --run-dir .run/custom_cases4/runs --max-model-calls 0 --allow-uncapped-gpu-hours
    python -B code/tools/validate_output.py .run/custom_cases4/predictions.csv --dataset .run/custom_cases4/dataset

Measured: 3/3 rows passed validation; 3 successful model calls, no failures or retries; 5,227 input tokens and 1,983 output tokens (7,210 total); 21.172 seconds instrumented model-client time and 22.202 seconds observed command wall time. The validator printed PASS: 3 rows satisfy structural checks.

The 63-test regression suite also covers future evidence exclusion, incomplete snapshots, exposed identifiers, restore risks, scope and policy handling, temporal identity, citations/order, cache-only replay with no provider calls, external-dataset preflight, and extraction/model failures including malformed, truncated, omitted, or invalid outputs. See evaluation_report.md for the executed test command and the target/sample limitations.
