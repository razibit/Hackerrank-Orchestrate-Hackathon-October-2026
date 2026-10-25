# Agent 6 read-only v15 cross-review

Reviewed: 2026-10-25T16:53:14+06:00
Live checkout: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26`, branch `main`
Scope: source diff, Agent 0 status, completed sample-v15 run summaries, usage checkpoint aggregates, and independent evaluator report. Did not inspect `sample_output.csv`, prediction contents, organizer truth, or per-call usage records. Did not run tests/inference or modify source/run artifacts.

## Trace pairing and temporal provenance

The new `_log_source()` pairing in `code/audit_agent/extractors.py` is conservative about identity: it requires one start and one readback completion in the same trace and operation, rejects conflicting resource/identity values, merges only whitelisted identity context, leaves completion state fields as the state, and retains both source-line locators (`trace:<id>:line:<start>+line:<completion>` and both `[line:n]` labels). Generic connection/retry/recovery rows do not contribute state. This preserves *source-location provenance*.

A temporal guard is missing. Pair selection checks uniqueness and conflicts, but does not establish that the start timestamp precedes the completion timestamp. A later start can therefore donate identity context to an earlier completion. This undermines temporal provenance and could contaminate state at `audit_at`. The prompt says “uniquely paired” but does not require chronological ordering. Recommend fail-closed unpairing unless both timestamps are known and start <= completion (or an equally authoritative ordering is available), and add reversed-time and missing-time regression cases before relying on this path for target output.

## Measured public-sample comparison

The independent evaluator report was created after `partial_predictions.csv` existed and confirms the prediction file remained unchanged. Labels were therefore used only for evaluation. Results are resolved-subset measurements and selection-biased.

| Metric | v14 | v15 | Change |
|---|---:|---:|---:|
| Resolved cases | 8/32 | 11/32 | +3 cases; unresolved 24 -> 21 |
| Status accuracy | 7/8 (87.50%) | 10/11 (90.91%) | +3.41 pp |
| Exact-step precision | 16/39 (41.03%) | 30/59 (50.85%) | +9.82 pp |
| Exact-step recall | 16/51 (31.37%) | 30/76 (39.47%) | +8.10 pp |
| Positional-field accuracy | 192/357 (53.78%) | 312/532 (58.65%) | +4.87 pp |
| Exact ordered sequence | 0/8 | 0/11 | no improvement |

All 11 resolved v15 rows still have at least one mismatch. The improvement is real on the public sample but does not support a release-quality claim or predict hidden-target accuracy.

## v15 usage

Checkpoint aggregate: 32 requests, 38 calls/attempts, 38 successes, 0 failures, 0 retries; 117,612 input + 47,480 output = 165,092 tokens; 414.672 seconds; 0.222503 accelerator-equivalent hours. Provider/model metadata: Microsoft Foundry / `openai--gpt-oss-120b`. USD cost unavailable. Versus v14, 3 fewer calls, 2,901 fewer tokens (~1.7%), and 31.156 fewer seconds (~7.0%). These are checkpoint aggregates; no usage-record contents were read.

## Remaining high-impact blockers

The 21 unresolved sample cases' reported first-stop groups are 7 evidence-category classification failures, 6 unresolved `SECURITY_AUDIT_LOG` conditional policies, 2 `BACKUP_ARCHIVE` conditional policies, 3 without subject-linked evidence, 2 missing grounded system/resource identifiers, and 1 supported only by workflow claims. These categories are reported as a first-stop breakdown, not necessarily independent root causes.

The evaluator highlights 7 positional `system_id`/`resource_id` mismatches, 5 missing `VERIFY_DATA_FLOW_DISABLED`, and 4 missing `VERIFY_RECORD_ANONYMIZED`. Exact ordered sequence remains 0/11. These indicate identifier grounding and completeness/ordering gaps even among resolved cases.

## Release status and recommendation

Agent 0's latest published status is timestamped 16:45+06 and predates the v15 completion/evaluation. At that snapshot, no 518-request v15 target run had started and no root `output.csv` existed. Do not infer whether the target run started afterward; obtain a fresh Agent 0 status before acting. The older v9 target blocker counts are not applicable to v15.

The package ZIP and global evaluation/usage reports remain timestamped 12:13+06, while current source changes are 16:39-16:40+06. The package inventory previously reviewed had 31 ZIP entries against 41 manifest paths, with ten manifest files absent. These artifacts are stale and need rebuilding from frozen final files, with manifest/CRC/size verification and refreshed reports. No v15 target result or output validation was available in this review.

Recommendation: keep release blocked. First close the timestamp-order pairing hole and regression-test it; then run a fresh public sample if needed to validate the fix and evaluate only after predictions are generated. Review Agent 0's current run/lease state before any target work. Complete a full target run, refresh exact usage/evaluation reports, validate root output, rebuild/verify archive and sanitized traces, then recheck the official submission requirements. Do not claim hidden-target accuracy.
