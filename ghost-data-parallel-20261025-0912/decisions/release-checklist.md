# Release checklist

Snapshot: 2026-10-25T16:25:45+06:00. Engine v12 status and sample figures below are reported by Agent 0; Agent 6 did not run tests/inference or inspect run/output files.

- [ ] Target v12 diagnostic run: recommended to obtain current first-stop blocker counts and target coverage. No v12 target result or blocker breakdown is in the published status/report files reviewed here. Do not reuse v9 counts as v12 diagnostics.
- [ ] Current validation: Agent 0 reports Engine v12, combined tests 112/112, and preflight passing. Agent 6 did not rerun them.
- [ ] Public sample: Agent 0 reports v10 at 10/32 resolved, 22 unresolved; resolved-subset status 9/10, exact-step precision 22/47, recall 22/62, positional fields 242/434, exact sequence 0/10. The v12 replay reused 43 responses and made 2 new policy calls with unchanged metrics. These are selected-subset results, not full-sample accuracy or target accuracy.
- [ ] Support-message policy: the previous boolean-metadata content-gate issue appears fixed in source and covered by tests; false metadata-only input remains unresolved and is excluded from the semantic second pass.
- [ ] Same-resource relevance: the new cutoff-aware exact-link override has a same-resource peer test. Keep resource state reconstruction grouped by physical scope.
- [ ] Historical target: coordination status/agent0.md remains v9 and reports 294 unresolved plus first-stop counts. Keep those numbers explicitly historical.
- [ ] Evaluation/usage reports: both remain timestamped 12:13+06 and describe earlier 65-test/sample/target runs. Refresh after target v12 and include the newest calls, measured tokens/time, and verified or unavailable cost.
- [ ] Package archive: code.zip remains timestamped 12:13+06 with 31 entries, while the manifest has 41. Ten current manifest entries are missing: code/audit_agent/policy_conditions.py, code/prompts/persistent_user_instructions.md, code/tools/agent5_diagnostics.py, code/tests/test_agent1_extraction.py, code/tests/test_agent2_identity.py, code/tests/test_agent3_policy.py, code/tests/test_agent4_model.py, code/tests/test_agent5_diagnostics.py, code/tests/test_agent5_legal_hold.py, and code/evaluation/agent5_sample_diagnostics.md. Rebuild from the final manifest and verify paths, CRC, and size.
- [ ] Release recommendation: not release-ready. Hold final claims until current target results exist, reports describe the v12 artifacts, and the rebuilt ZIP matches the manifest.
- [ ] Submission portal: no current portal state or upload has been verified.

No run outputs or sample labels were accessed for this review.
## 2026-10-25 18:09:29 +06:00 — Agent 3 one-loop planner replay rejected

Verified in the updated evaluation report: Agent 0 tested the one-loop planner in an isolated v15 copy using cache-only replay (zero new model calls). Coverage and status stayed 11/32 and 10/11. Exact steps changed 30/59 to 32/59, recall 30/76 to 32/76, and positional fields 312/532 to 315/532. The official partial evaluator rejected three non-empty verification citations in INCOMPLETE case_27; future verification steps in INCOMPLETE rows require an empty evidence_id. The planner candidate is rejected and not integrated. The v15 source/package remain the release candidate; no change to the active process or archive is requested.

## 2026-10-25 18:17:03 +06:00 — trace archive prompt-preparation exclusion verified

Read-only verification of the corrected root agent-trace.zip: 16 entries, CRC check passed, five ChatGPT Markdown exports, and the separate 007-2026-10-25-Create Parallel Agent Prompts.md export is absent. The included README and import_manifest both describe five ChatGPT exports and state that prompt-preparation conversations were excluded. Agent 0 reports the prior ZIP is retained separately as a backup and root log.txt was left untouched. Agent 6 did not restore the export or modify trace archive contents, root log, source, or active run.
