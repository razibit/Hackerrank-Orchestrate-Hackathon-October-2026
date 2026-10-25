# Agent 5 status

State: v15 public-sample evaluation and v14 paired cross-evaluation complete; no runtime code changed.

Last updated: 2026-10-25 17:36:22 +06:00
Inbox: inbox/agent5/20261025T113233Z/

## Completed

- Recomputed v9 public-sample metrics from the pre-existing 14-row partial prediction file using the existing evaluator and an independent Agent 5 evaluator. The prediction file hash and modification time were stable across evaluation.
- Validated all 14 supplied rows against their matching sample requests with validate_output.py and the existing contract rules. This is subset validation only; it is not a 32-row sample or 518-row target validation.
- Added and ran six Agent 5 tests; the six existing contract tests also passed.
- Read-only audit of the final unresolved_cases.txt found 294 first-stopping blockers; family triage and integration recommendations are in blocker-audit.md and integration-memo.md.
- Staged code, sanitized aggregate report, exact commands/results, a same-hash sample prediction snapshot, minimal validation-request sidecar, synthetic regression, and prompt documents.

## Key measured findings

- Sample coverage 14/32; status 14/14; exact-step precision 35/67; recall 35/87; positional fields 358/609; exact sequences 0/14. These resolved-row metrics are selection-biased.
- Verification deficits account for 20 fewer operations: 13 VERIFY_RECORD_ABSENT, 6 VERIFY_RECORD_ANONYMIZED, 1 VERIFY_RECORD_PRESENT.
- Three retention-labeled VERIFY_RECORD_PRESENT steps scored 0/3 exact matches. Two incomplete proposals have no same-resource finding; the only complete citation is a PDF with no extracted legal/hold/retention/active/expiry markers. Treat as unresolved risk, not a proof of no hold.
- Agent 0 completed all 518 requests, but 294 remain unresolved and no root output.csv was produced. No hidden-target accuracy is available.

## Logging blocker

The session metadata identifies Codex Desktop and provider OpenAI, but no exact runtime model identifier is available. Per AGENTS.md and the user instruction, no model placeholder or guess was recorded. log-fragment.txt records this blocker; the live root log remains Agent 0-owned.

## 2026-10-25 17:36:22 +06:00 — v15 public-sample cross-evaluation

- Independently scored the pre-existing .run/sample_v15/partial_predictions.csv after confirming the file existed and no sample-v15 prediction process was active. Its SHA-256 stayed 12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565 before and after evaluation.
- Official evaluation and subset contract validation passed: 11/32 coverage, status 10/11, exact-step precision 30/59, recall 30/76, positional fields 312/532, exact sequences 0/11; 11 supplied rows passed contract validation.
- Paired v14/v15 evaluation on eight shared cases found no aggregate status, step, field, or order improvement: 7/8 status, 16/39 exact-step precision, 16/51 recall, 192/357 fields, 0/8 exact sequences for both. v15 adds three resolved cases; whole-subset gains are selection-dependent.
- General fixes and the existing diagnostic field-denominator caveat are in inbox/agent5/20261025T113233Z/agent5_v15_cross_evaluation.md. Detailed and reproducible outputs are in the same inbox.
- No inference, source edits, target-v15 access, root-report changes, or output.csv changes; no model/provider calls. A log fragment is staged; root log remains Agent 0-owned.
