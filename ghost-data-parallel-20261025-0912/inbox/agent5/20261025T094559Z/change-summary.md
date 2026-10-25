# Agent 5 change summary

## Scope

This work used the already-generated v9 public-sample partial prediction file. It did not run inference, create missing predictions, inspect the active target cache/checkpoint, edit runtime agent modules, change the live checkout, or read organizer truth.

## Added

- code/tools/agent5_diagnostics.py: validates an existing partial CSV before opening public sample answers, recomputes official sample metrics, reports field and operation mismatches, summarizes repeated patterns without case or person identifiers, and records prediction timestamp/hash stability. Its retention probe reads only cited participant evidence and reports aggregate markers.
- code/tests/test_agent5_diagnostics.py: aggregate scoring, identifier minimization, and retention-evidence probe checks.
- code/tests/test_agent5_legal_hold.py: a synthetic deterministic-boundary regression. A present register row with a future retention date remains unresolved for the distinct active-hold condition; unresolved policy blocks treatment, while an explicitly grounded TRUE condition permits retention.
- code/evaluation/agent5_sample_diagnostics.md: sanitized public-sample report with no per-case IDs.

## Reproduced sample results

- Coverage: 14/32 (43.75%), selection-biased.
- Status accuracy: 14/14 (100%).
- Exact-step precision: 35/67 (52.2388%).
- Exact-step recall: 35/87 (40.2299%).
- Positional-field accuracy: 358/609 (58.7849%).
- Exact sequence accuracy: 0/14; every resolved case had a status or sequence mismatch.
- Official validator and repository contract checks passed for the 14 supplied predictions against their matching public requests. This does not validate a complete 32-row sample or 518-row target output.

## Defect diagnosis

The predicted operation multiset is short by 20 steps, all in verification: 13 VERIFY_RECORD_ABSENT, 6 VERIFY_RECORD_ANONYMIZED, and 1 VERIFY_RECORD_PRESENT. No predicted operation count exceeds its sample reference count. Positional system/resource mismatches and verification-tail alignment are also frequent; positional field rates count missing/extra steps as seven mismatches, so they are not independent field-extraction rates.

The saved sample predictions still contain three retention-labeled VERIFY_RECORD_PRESENT steps; none is an exact full-step match to the public sample answer. Two incomplete cases have no same-system/resource finding for the proposed present check. The one complete check cites a two-page PDF whose extracted text has no matches for legal, hold, retention, active, present, or expires. This supports an unresolved/unsupported retention claim in the sample output, not proof that no hold exists.

The baseline evidence-classification prompt broadly says direct dates can establish retention conditions, while the deterministic policy-condition resolver has no legal-hold branch. A category-specific rule should make clear that record_state=PRESENT and a future retention_until date do not establish an active legal hold. Keep the hold unresolved unless scoped, time-valid source evidence explicitly supports it.

## Completed target run

Agent 0 completed v9: 518 processed, 294 blocked, 224 checkpointed rows (80 COMPLETE, 134 INCOMPLETE, 10 NOT_APPLICABLE), and no root output.csv. The unresolved-family audit is in blocker-audit.md. Its entries contain first-stop reasons but no evidence excerpts, so they cannot be assigned definitively to extraction failure versus absent evidence case by case.

Final measured target usage: 724 provider attempts, 723 successful, 1 failed, 1 retry, 445 cache hits, 278 misses, 1,799,020 input tokens, 820,448 output tokens, and 2,619,468 total tokens. This is processing usage only; there is no complete target CSV and no target accuracy claim.

## Logging limitation

No valid AGENTS.md log entry could be staged because the authoritative Codex Desktop session metadata did not expose the exact model identifier. The prompt prohibits guessed or placeholder model names. A logging-blocker note is staged in log-fragment.txt; the live root log remains under Agent 0 ownership.

## Prompt preservation

The exact attached Agent 5 task prompt and the persistent user instruction text are staged under prompts/. The separate prompt-preparation conversation is not included.
