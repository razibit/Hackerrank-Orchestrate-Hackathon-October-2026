# Read-only v9/v10 sample prompt comparison

Compared the public-sample partial prediction files and unresolved diagnostics, the immutable baseline prompts/model, and the current live prompt/model files. No `sample_output.csv`, labels, response cache, checkpoint contents, or target output was opened. No inference or tests were run; no source/runtime files were changed.

## Findings

- v9 artifact `.run/target_v9/sample_partial_predictions.csv` contains the 14 resolved IDs supplied in the request. v10 `.run/sample_v10/61a7f1c04aa9f06477bdb187a551c10c632673d46a77a244f2aaf148137db957/partial_predictions.csv` contains the supplied 10 IDs. Its unresolved diagnostics list cases 08/21/29 as material-category unresolved and case 10 as `SECURITY_AUDIT_LOG` condition unresolved.
- The v9 predictions for 08/21/29 each proposed a `legal_retention_service` `VERIFY_RECORD_PRESENT` step. Cases 08 and 29 gave that step no evidence ID; case 21 cited `evidence_27`. The v10 evidence prompt and model guard now require same-observation, hold-specific evidence before classifying a retention row as `LEGAL_HOLD_RECORD`; row presence and a future retention date alone cannot establish an active hold. This is a plausible, direct cause of those three drops and is consistent with removing unsupported retention claims.
- Baseline and current structured schemas (`INTENT_SCHEMA`, `OBSERVATION_SCHEMA`, `POLICY_CONDITION_SCHEMA`) are structurally equal. The model change adds local schema validation, exact ID checks, response splitting, and the legal-hold guard; malformed outputs may now fail closed, but schema shape changes do not explain a valid unresolved category by themselves.
- The v10 output timestamp is after the Agent 4 candidate was staged; current live prompt and model hashes match the Agent 4 candidate, while baseline prompt hashes differ. This supports attribution to the integrated candidate, but the sample run directory has no readable source manifest proving the exact runtime snapshot. For case 10, the more explicit rule to leave unsupported conditions unresolved could contribute; the first-stop reason alone cannot tell whether its source content actually supports the condition.

## Recommendation

Do not relax the legal-hold rule or broadly force a material category or security condition to resolve. The v9 steps for cases 08/29 lack source IDs, and the cited source for case 21 does not by itself establish an active hold. Keep the unresolved outcomes unless a source-grounded review shows a specific, generalizable category/condition was supported; only then add a narrow rule and synthetic regression. No safe correction is justified by these artifacts alone.

The output schemas are unchanged. No run-level accuracy or label comparison was used.
