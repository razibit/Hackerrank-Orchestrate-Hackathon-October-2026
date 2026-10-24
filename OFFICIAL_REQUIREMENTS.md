# Verified official requirements

Checked 24 October 2026, Asia/Dhaka. Official requirements outrank AI-generated strategies.

## Evidence and access

- **O1:** [Challenge portal](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists): web retrieval failed; browser redirected to login. Authenticated form, live cutoff and edition overrides were not inspected.
- **O2:** [Official repository](https://github.com/interviewstreet/hackerrank-orchestrate-october26/tree/0eddbbd33f682eae0a2770d67412af8a3cf4af20): upstream main and local HEAD both resolve to `0eddbbd33f682eae0a2770d67412af8a3cf4af20`. README, problem statement, AGENTS and trace instructions were retrieved using the GitHub connector and match local text after newline/trailing-whitespace normalization. [Frozen copies](research/official/README.md).
- **O3:** [Official help](https://help.hackerrank.com/articles/3728112689-hackerrank-orchestrate?lang=en): web retrieval failed, browser rendered article successfully. Participation, uploads, scoring and October timeline were read. Troubleshooting accordions were not expanded; no policy inferred from headings.
- **O4:** [Behind the Scenes](https://www.hackerrank.com/blog/behind-the-scenes-of-hackerrank-orchestrate/): accessible historical May judging analysis, not confirmed October subweights.
- **O5:** [May event](https://www.hackerrank.com/hackerrank-orchestrate-may26): accessible historical event; ticket task, dates and rewards do not govern October.
- **O6:** [October event](https://www.hackerrank.com/hackerrank-orchestrate-october26): accessible schedule, rewards and workflow.

## Participation, time and scoring

O3 confirms an individual hackathon: work independently and submit your own work. Prerequisites include registration/account, preferred AI coding tools, stable internet, microphone and camera. Language, model, framework and tools are flexible, subject to event rules.

Start: **24 October 2026 at 12:30 UTC / 18:30 Asia/Dhaka / 18:00 IST**. The event describes a 24-hour format. Adding 24 hours suggests 25 October 18:30 Dhaka, but this is a **nominal calculation**, not a verified portal cutoff. Repository timer is explicitly unconfigured. The interview opens after submission; its completion deadline remains unverified. Live evaluation: 26–27 October; results: 27 October. Do not reuse old exported countdowns.

O3 general scoring is 30% code, 30% output, 30% interview, 10% transcript, each signal 0–100. It explicitly warns that edition-specific rules can vary. October tie-breaker order, exact hidden formula, runtime/API/token limits and resubmission limits were not verified. Absence in inspected documents does not establish unlimited use.

O6 advertises $1,200 first-place cash and Codex credits for qualifying top-three builders using Codex. All eligibility terms were not independently established.

## Actual task and dataset

Build a terminal-runnable AI-powered deletion-audit agent. Decide whether deletion was authorized; resolve current/historical identity; establish resource state at `audit_at`; apply conditional supplied policy; discover remaining data and recreation risks; propose ordered remediation and verification. Do not execute deletion in real services.

Use participant-facing `dataset/` only for inference. Public sample labels are evaluation-only. Organizer truth, generator internals, case-family shortcuts and hardcoded golden labels are prohibited. Both Python entry points are empty; Python is optional.

| File | Measured rows | Role |
|---|---:|---|
| deletion_requests.csv | 518 | Target requests |
| sample_deletion_requests.csv | 32 | Public samples |
| sample_output.csv | 32 | Reference answers, evaluation only |
| user_identities.csv | 850 | Current snapshot |
| user_audit_log.csv | 306 | Historical identity changes |
| system_activity.csv | 4,011 | Global operational claims and events |
| deletion_rules.csv | 15 | Conditional policies |
| evidence_files.csv | 94 | Manifest, not case-membership map |
| dataset/output.csv | 0 | Header-only template |

Evidence formats: 24 SQL, 28 JSON, 26 logs, 11 PNG, four PDFs/seven pages, one TXT. SQL is SQLite-compatible. Structural parsing does not prove correct semantic extraction.

Input columns: `case_id,email,requested_at,reported_status,reported_at,audit_at,request_text`. Reported status/operation results are claims. Use no post-cutoff evidence; internal event/observation time also matters. Preserve policy-required records and stable tombstone references. Active synchronization and unsafe restoration can make deletion incomplete.

## Output contract

Write **checkout-root** `output.csv`. Exact header: `case_id,deletion_status,steps_json`. Exactly 518 data records, one per target ID, lexically sorted. Count parsed CSV records, not physical lines.

- `NOT_APPLICABLE`: no authorized deletion; `steps_json=[]`.
- `COMPLETE`: evidence-backed verification only.
- `INCOMPLETE`: findings, complete proposed remedies and future checks.

Each step has exactly `step_no,phase,system_id,resource_id,operation,state,evidence_id`; step numbers are consecutive integers starting at 1. JSON array order matters; key order and whitespace do not.

| Phase | Operation order | Corresponding states |
|---|---|---|
| FINDING | REPORT_REMAINING_RECORD; REPORT_EXPOSED_PII; REPORT_ACTIVE_DATA_FLOW; REPORT_RESTORE_RISK | PRESENT; PRESENT; ACTIVE; ACTIVE |
| REMEDIATION | DISABLE_DATA_FLOW; BLOCK_RESTORE; DELETE_RECORD; REDACT_RECORD; ANONYMIZE_RECORD | DISABLED; BLOCKED; ABSENT; REDACTED; ANONYMIZED |
| VERIFICATION | VERIFY_RECORD_ABSENT; VERIFY_RECORD_PRESENT; VERIFY_RECORD_REDACTED; VERIFY_RECORD_ANONYMIZED; VERIFY_DATA_FLOW_DISABLED; VERIFY_RESTORE_BLOCKED | ABSENT; PRESENT; REDACTED; ANONYMIZED; DISABLED; BLOCKED |

Sort by phase, published operation rank, system_id, resource_id; number afterward. Findings and COMPLETE verification cite a valid pre-cutoff file_id/activity_id/audit_id that actually proves the claim. All INCOMPLETE remediation/verification use an empty evidence_id. A recognized ID alone does not prove relevance.

## Submission

O3: three uploads, maximum **50 MB each**, followed by a 30-minute AI interview. O2 names `code.zip`, root `output.csv`, root `log.txt` in chat_transcript. README explicitly directs reports under `code/evaluation/`:

- evaluation_report.md: status, step/field and sequence accuracy, at least three participant-created cases, failures and improvements.
- usage_report.md: final full-dataset run provider/model, calls, input/output tokens, totals/averages, estimated total/per-request cost; per-model and overall totals.

Write required metrics/cases/cost tables in Markdown and prompts in source or Markdown. README says automated code evaluation ignores raw CSV/TSV/JSON/JSONL/SQL/log data. This does not prohibit runtime JSON assets; explain observable behavior in source and Markdown.

Include runnable source, README, prompts, necessary dependencies/config and reports. Exclude supplied data, environments, caches, credentials, sensitive configuration and nested archives. The separate trace instructions request `agent-trace.zip`: preserve sanitized original traces separately, never nest it in code.zip. Its extra upload channel remains unresolved.
