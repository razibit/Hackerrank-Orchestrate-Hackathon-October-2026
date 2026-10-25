# Prioritized integration memo for Agent 0

## 1. Close the verification-step gap first

The resolved sample has 20 fewer operations than its reference, and every deficit is a verification step: 13 VERIFY_RECORD_ABSENT, 6 VERIFY_RECORD_ANONYMIZED, and 1 VERIFY_RECORD_PRESENT. Predicted counts for all other operations match their reference counts. Preserve every required postcondition through planning and serialization, then apply canonical phase/operation/system/resource ordering. This is the clearest general score opportunity in the measured subset.

The sample has 0/14 exact sequences, so status accuracy alone does not establish step quality. Positional field accuracy counts missing or extra steps as errors in all seven fields. Several positional operation substitutions therefore likely reflect a shortened or shifted verification tail as well as operation selection.

## 2. Keep system/resource pairs tied to evidence

The most repeated positional pattern is a joint system_id and resource_id mismatch (9 occurrences). Keep each locator pair together from the cited observation through finding, remediation, and verification. Avoid filling one field from a nearby record or another physical scope.

## 3. Require direct evidence of an active legal hold

The saved sample output has three retention-labeled VERIFY_RECORD_PRESENT steps and none exactly matches the public sample answer. Two incomplete cases lack a same-resource finding. The one completed step cites a PDF with no extracted legal/hold/retention/active/expiry markers. Treat these as unresolved evidence risks.

The evidence-classification prompt's general date-based retention wording can be read as supporting a legal hold, but the policy requires an active supplied hold. Narrow the prompt and/or add deterministic category-specific validation: a present register row or future retention_until alone is insufficient. Coordinate with the prompt/policy owners; Agent 5 has not edited their files.

Negative regression: LEGAL_HOLD_RECORD, record_state=PRESENT, future retention_until, no explicit active hold must remain unresolved/false and must not trigger retention.
Positive regression: an explicit, subject-linked, time-valid active-hold record should satisfy the supplied RETAIN rule.

Agent 5's synthetic test covers the deterministic unresolved boundary only; it does not call the model or test its prompt fallback.

## 4. Keep the release gate closed

Agent 0 completed 518 requests with 294 blocked; 224 cases were checkpointed as 80 COMPLETE, 134 INCOMPLETE, and 10 NOT_APPLICABLE. No root output was written. Keep the full release gate closed until unresolved cases are addressed. The family audit is in blocker-audit.md; several first-stop families remain mixed because their list entries omit source evidence fields. Do not convert them into guesses. The 14 resolved public sample rows remain selection-biased and do not support a hidden-target accuracy claim.
