# Specialist candidate review

Reviewed: 2026-10-25T15:46:29+06:00
Reviewer: Agent 6
Authority: Agent 0 owns integration and release. No candidate files were copied or applied.

## Agent 1 — extraction

Delivery: inbox/agent1/20261025-1534/ contains extractors.py, test_agent1_extraction.py, change-summary.md, test-measurement-results.md, and log-fragment.txt. This matches Agent 1's assigned extractor and extractor-test scope.

Assessment: The diff stops treating a retention-register name/date as an active legal hold, retains the six evidence_27 rows as separate PRESENT snapshots, and adds source_path provenance. It preserves subject splitting. The targeted tests passed 2/2. The isolated full suite had 71/72 passing because an existing test still expects the old LEGAL_HOLD_RECORD behavior. That assertion needs an intentional update if Agent 0 integrates the change. Agent 1's evidence measurement reports that evidence_27 describes disputed tax/order retention without active-hold status; this is a source-grounded reason to keep those rows unresolved.

Dependency: Agent 4's prompt guard and a deterministic engine condition guard are still needed because the existing engine can let model TRUE survive for legal holds. Measure any source_path prompt-token effect after integration; no token delta was measured here.

## Agent 2 — identity and time

Delivery: inbox/agent2/20261025-1534/ contains identity.py, test_agent2_identity.py, change-summary.md, and log-fragment.txt. The source change stays within assigned identity.py; data.py is unchanged.

Assessment: The patch avoids creating an unbounded duplicate old_value alias when the preceding same-user, same-field event already proves that normalized alias interval. It also rejects requests after audit_at and future event/observation instants. Tests cover offsets, history/reassignment, overlapping owners, invalid event times, future cutoffs, and duplicate names. Static review found no blocking issue.

Reported checks: 8 focused and 78 full-suite tests passed in Agent 2's isolated workspace. Its 518/518 result is identity-email resolution only and does not mean evidence coverage or prediction accuracy. Agent 6 did not rerun tests. The baseline submission manifest omits the new test.

## Agent 3 — policy conditions

Delivery: inbox/agent3/20261025-0937-UTC/ contains policy.py, new policy_conditions.py, test_agent3_policy.py, two prompt files, test outputs, change-summary.md, engine-integration-proposal.md, log-fragment.txt, and alert-request.md.

Ownership: policy.py and policy tests are assigned. policy_conditions.py is a new source module outside Agent 3's listed ownership; the prompt files are in Agent 4's prompt ownership. Agent 3 has not changed engine.py. The helper should not be treated as an authorized drop-in; Agent 0 must decide whether to assign/rehome it or require a patch in policy.py, and Agent 4 should own prompt-file changes. The engine adapter remains a proposal.

Reported checks: 7 focused and 77 full-suite tests passed in Agent 3's isolated workspace. No model, sample, or target evaluation was run. This suite is separate from Agent 1 and Agent 2 workspaces.

Static review: false-condition action validation follows the participant-facing rules. The deterministic helper makes missing active-hold status and generic security retention dates UNRESOLVED. Two tests are still needed before accepting the helper:
1. support_message_has_content includes boolean metadata keys such as contains_shared_context and treats normalized false as content because false is not in its non-content values (policy_conditions.py lines 30–34, 70–80). The existing test covers email-only and message text but not false flags. Add a regression so metadata flags alone do not masquerade as message body/context; resolve only if the policy and source prove their meaning.
2. The LEGAL_HOLD_RECORD branch checks structured status fields and ignores raw_text. If an evidence document explicitly states that a hold is active but extraction did not populate one of those fields, the helper returns UNRESOLVED. Either ensure extraction produces a validated hold-status field or handle the direct textual evidence with a grounded rule; do not let an unsupported model result override uncertainty.

The full-suite 77/77 result predates Agent 1's extractor patch and does not include that patch's expected legacy assertion failure.

Logging: Agent 3 correctly staged an explicit logging blocker because its current session lacks an authoritative exact model ID. Do not append placeholders or substitute the deployment/model selected by another session.

## Agent 4 — model and prompts

Latest delivery: inbox/agent4/20261025-154511/ supersedes 20261025-153720/. It contains model.py, all three assigned prompt files, test_agent4_model.py, change-summary.md, exact targeted/full test outputs, usage-records.md, and log-fragment.txt. Source ownership remains within model.py, prompts, and its new test; the engine proposal is not part of this latest delivery.

Assessment: The candidate adds local schema validation, exact ID/type correlation, bounded batch splitting for truncation or ID mismatch, and corrected retry accounting. Prompts strengthen original-language negation, source grounding, content-based support retention, and unresolved handling. A deterministic guard prevents a present retention row or future retention date alone from being promoted to LEGAL_HOLD_RECORD/TRUE. It resolves explicit same-observation hold status or supported English text and keeps conflicting evidence unresolved. Synthetic tests cover retention-only false positives, active/released/conflicting hold facts, parser/schema failures, IDs, retries, cache versioning, and prompts.

Reported checks: 18 targeted and 88 full-suite tests passed in Agent 4's isolated workspace. It reports zero inference calls and no sample/target evaluation or live model-quality delta. Recursive splitting is bounded but can increase request count and latency: the summary estimates at most 39 calls for a 20-item intent batch and 9 for a batch of 5, before per-call retries. The new test is absent from the baseline package manifest.

Logging issue: the staged fragment still says model=GPT-6, a family descriptor rather than the exact model identifier required by AGENTS.md. Correct only from Agent 4's authoritative runtime metadata; otherwise retain the logging blocker. Do not substitute Agent 6's model ID or the Foundry deployment.
## Combined integration dependencies

- Agent 0's completed v9 run remains blocked: 294 of 518 cases unresolved; no root output.csv.
- The Agent 1 extraction, Agent 4 prompt, and Agent 3 policy/engine proposals address the same legal-hold failure. Consolidate them under Agent 0 engine ownership; do not apply duplicate adapters independently.
- Agent 3 and Agent 4 each propose an engine-level legal-hold guard. Select one implementation design and test it against explicit active, inactive, missing, conflicting, future, and text-only evidence.
- Agent 1's old extraction assertion must be updated when integrating its new unresolved snapshot behavior.
- New tests and modules are absent from the current allowlist. Update SUBMISSION_MANIFEST.md for every retained artifact.
- Specialist suites were run in separate copies. No combined suite, sample re-evaluation, or post-fix target run has been reported.

## Recommendation

The Agent 1, 2, and 4 changes are reviewable candidates, not integrated fixes. Agent 3's policy helper needs ownership resolution and the two static-review gaps above addressed. Agent 0 should use the completed target blocker report to sequence integration, run a combined test suite, then measure sample and a fresh full target run. Keep unresolved evidence fail-closed and report actual usage/cost without extrapolation.