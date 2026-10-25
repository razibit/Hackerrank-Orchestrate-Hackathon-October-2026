# Contest architecture and engineering priorities

## Objective

For each of the 518 `deletion_requests.csv` rows produce `{case_id,deletion_status,steps_json}`, strictly grounded in participant-facing data and case-specific `audit_at`.

## Recommended architecture

1. **Intent interpreter:** classify deletion authorization from natural-language `request_text`, including multilingual requests, negation, and access/rectification/export/opt-out intents. Use a language model for ambiguous cases; log model token usage and optionally cache classification by content hash. Never assume `reported_status` implies authorization.
2. **Identity resolver:** join `email` to current identity and to all historical `old_value/new_value` events; track names, phone numbers, email hashes and aliases. Be careful with reused identifiers and unrelated people. Treat historic identifiers as candidate aliases, not proof of case ownership without stable links.
3. **Evidence ingester:** parse SQL snapshots with SQLite, structured JSON and service readbacks, logs, PDF text, and images via an appropriate vision-capable model. Index facts by `file_id`, `system_id`, `resource_id`, identifiers, observation time and provenance. Do not make decisions solely from the manifest.
4. **Temporal state resolver:** for each case/resource, evaluate available snapshots and explicit readbacks at or before `audit_at`, reconcile contradictory evidence, assess whether state is current enough and treat activity `reported_result` as an unverified claim. Investigate failover/region-specific replicas individually.
5. **Policy engine:** apply `deletion_rules.csv` with conditions, including shared support messages, security retention, legal holds, backup restore-block requirement, and tombstones retaining only stable references. Do not treat backup as `DELETE` where retention applies.
6. **Planner:** build findings, then disable relevant flows/block restores, then treat offending records, then verify all remediated and required retained states. Generate the allowed operations only.
7. **Evidence and output validator:** each existing-state finding or `COMPLETE` verification must cite valid proof at/before `audit_at`; planned remediation/future verification cites `""`. Sort by phase, operation rank, system ID, resource ID, then number `step_no` consecutively. Format exact CSV.
8. **Evaluator:** run on 32 official public samples, report status accuracy, exact step match, step precision/recall/F1, aligned-field accuracy and sequence accuracy. Add three synthetic adversarial cases (not counted as official labeled accuracy).
9. **Metering:** capture actual model invocation counts and provider-reported token usage, track retry/cache hit rates, estimate cost using the actual model's published price. Report final full-dataset run; don't invent token counts.

## Critical failure modes

- `audit_at` leakage: evidence from later time used to decide an earlier case.
- Assuming a successful delete event proves absence while a replica still contains data.
- Blindly fuzzy-matching similar-looking emails belonging to other people.
- Missing historical hashes, alias emails and restored copies.
- Mistaking an intentionally retained security record or tombstone for policy violation.
- Treating a retained backup with restore enabled as safely compliant.
- Failure to disable a sync before planning dependent deletions.
- Incorrect status with otherwise plausible steps; wrong `file_id`/`activity_id`/`audit_id`.
- Missing a verification step for already-compliant but required retained records.
- Incorrect operation ordering or `evidence_id` nonempty on planned steps.

## Iteration gates

**Gate A:** sample request classification, identity joins and data indexing pass unit tests.

**Gate B:** sample output matches canonical sample *without using the labels in predictions*; report per-case diffs and investigate every mismatch.

**Gate C:** 518 row output passes `validate_output.py` and reruns deterministically from source.

**Gate D:** README, evaluation report, usage report, transcript and output artifact all pass submission checks.

Use the official sample labels only for offline evaluation. Do not use hidden organizer labels, case-number patterns, or code paths that copy sample canonical steps at inference time.
