# Conflict resolution and decisions

Official contract decisions are established below. Implementation choices remain provisional until full semantic coverage closes.

| ID | Competing claim | Evidence and resolution |
|---|---|---|
| D01 | S4 says production-ready and 32/32 verified | Its Python entry point prints a message. No complete ingestion/orchestration/prediction writer exists. Five focused probes fail. Preserve as partial reference, reject success claims. |
| D02 | S5 code/transcript weights 20%/20% | Browser-read official help gives 30%/10%, with edition-override caveat. |
| D03 | S4 says nine PNG, 22 SQL, 29 logs | Actual manifest has 11 PNG, 24 SQL, 26 logs, 28 JSON and one TXT. Use measured counts. |
| D04 | S4 says case_09 has only three backup steps and backup_vault | Actual sample has five steps, including account absence and retained security verification; system is backup_service. Reject stale description. |
| D05 | S4 anonymizes analytics_9914 | Actual case_12 requires DELETE_RECORD and VERIFY_RECORD_ABSENT. evidence_01 describes a contact lookup with email_opt_in and historical hash. System/prefix does not establish ANALYTICS_PROFILE. Complete related corpus review before final category mapping. |
| D06 | Fixed deterministic pipeline vs autonomous/complex agent | Propose one bounded investigator for semantic tasks, with deterministic identity/time/policy/output controls. No guaranteed architecture score; benchmark after review. |
| D07 | S4 missing identity/evidence => NOT_APPLICABLE | Official status concerns authorization. Keep internal unresolved state; investigate or block release rather than fabricate a public answer. Probe reproduced. |
| D08 | S4 claims cutoff-aware identity graph | All aliases are accumulated before cutoff; only audit IDs are filtered. Future-alias probe fails. Track validity/availability and reused aliases by stable subject. |
| D09 | S4 allows empty COMPLETE proof | Official contract requires citation; reference validator accepts empty evidence_id. Reject exception; S2 validator is stricter. |
| D10 | S2 vs S3 validators/evaluators | Prefer S2 baseline: aware timestamps, strict types, exact coverage and all INCOMPLETE phases. S3 compares timestamps as strings and evaluator collapses duplicate IDs/ignores extras. Neither proves semantic correctness. |
| D11 | S3 indexer keeps only resource-bearing log lines | Identity is often on started-query lines and resource on completed-query lines. Preserve full context and join trace_id/source/system/time. Existing index output cannot establish complete coverage. |
| D12 | Latest record globally vs replica drift | Reduce by physical replica/table/region scope. New primary absence cannot erase still-present replica. Capture/availability and observation time are separate. |
| D13 | Dependency-first plan vs canonical lexical order | Check safe dependencies internally; serialize by explicit problem-statement order. Actual case_24 orders account_service before search_service DELETE_RECORD. Seek clarification for a concrete irreconcilable dependency. |
| D14 | evaluation/ shorthand vs code/evaluation/ | README explicitly instructs code/evaluation/ and packages README+code. Use that layout; include root runtime dependencies separately if needed. |
| D15 | log.txt vs original trace ZIP | Preserve both; log.txt goes in documented transcript slot. Confirm additional channel. Never nest trace archive in code.zip. |
| D16 | S2 four-w challenge URL | Upstream commit 0eddbbd fixes typo. Keep source snapshot; use working three-w URL. |
| D17 | S5 replied/escalated output and injection=>invalid | Wrong task schema. Determine deletion authorization even with hostile embedded text; isolate instructions and constrain tools. Regex detection alone is not a defense. |
| D18 | S4 95–99% accuracy, seconds runtime, <$0.30 and interview anecdotes | Unsupported by supplied runnable evidence. Reject numerical predictions and never repeat invented regressions as personal experience. |
| D19 | Hardcode vision_cache.py for judge visibility | Cache extracted facts as runtime data keyed by source/model/prompt hashes. Explain mechanism in source/Markdown; avoid dataset-specific verdicts disguised as implementation. |
| D20 | Old countdowns/current deadline | Official start verified; authenticated cutoff is not. Nominal 24-hour calculation remains labeled. |

Equal initial consideration was maintained. S1 contributes ownership/interview discipline; S2 provides strong contract tools and honest limits; S3 adds useful extraction/metric scaffolding; S4 offers typed immutable observation ideas despite serious defects; S5 offers operational habits despite historical task mismatch.
