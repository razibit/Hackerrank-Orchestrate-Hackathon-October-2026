# Consolidated research

**Coverage status: COMPLETE.** All 74 unique participant evidence files in the review ledger have full analyst coverage across 213 planned chunks and 18,704 physical lines. All source digests match; starter/check-out pairs match after newline normalization. The [coverage report](research/review-completion/coverage-report.md) and [progress ledger](research/review-progress.json) are the audit trail. This closes source investigation, not implementation or predictive evaluation.

## Cross-source synthesis

All five sources favor model interpretation with deterministic constraints, evaluation, authentic ownership and clear documentation. The official task makes this concrete: authorization first; current/historical identities; pre-cutoff facts; conditional policy; remaining copies/recreation risks; valid proof and exact ordered steps. A schema pass does not establish factual accuracy.

**S1 exported conversation:** progresses from pre-release generic advice to challenge-specific preparation. Keep coding-assistant vs runtime API access distinction, iterative diagnosis, and Decision → Reason → Implementation → Evidence → Limitation interview structure. Prior countdowns, anecdotes and scoring assertions need current verification.

**S2 work-mode starter:** START_HERE, preparation/REQUIREMENTS, FIRST_PROMPT, SYNTHETIC_CASES and VERIFICATION correctly disclose empty main.py, unexecuted reasoning fixtures and comparator-only tests. Its dataset matches the existing workspace after text newline normalization. Preserve one runtime dataset. The imported source log's unavailable model metadata must not be rewritten into invented values. Current session metadata identifies gpt-6.1-sol.

**S3 chat-mode starter:** ENGINEERING_PLAN largely aligns with the real task. JSON traversal, SQL extraction and sample metric scaffolding are reusable ideas. Hazards include unguarded manifest paths, unrestricted executescript, dropped log context, heuristic nested-object selection and no actual image interpretation. install_starter.ps1 force-overwrites tools/reports; it was inspected, not run. Explicit selective copying is safer here.

**S4 Gemini:** immutable observations/steps and canonical operation tables are useful designs. Supplied code is partial, despite claimed full verification. Strategy mixes helpful concerns with wrong counts/sample descriptions and unsupported performance claims. Do not install as main.py or reuse invented interview stories.

**S5 battle plan:** pre-challenge ticket-routing style guidance. Keep retries, README clarity, iterative testing, submission buffer and interview ownership. Discard response/escalation schema, injection-implies-invalid rule, speculative scores and mandatory second provider.

## Direct findings

- Public labels: 10 COMPLETE, 22 INCOMPLETE, zero NOT_APPLICABLE, 193 steps and all 15 allowed operations. Public samples cannot validate the non-deletion branch or predict target distribution.
- Actual case_09 includes compliant account/security verification beyond backup remediation. case_29 includes 14 steps and checks both already-compliant and remediated resources. Build the verification set from grounded required resources, not violations alone.
- case_12 deletes analytics_9914. Resource prefix/system cannot determine policy category; inspect content/collection/event role. evidence_01 has contact lookup, email_opt_in and historical-hash correlation.
- customer_accounts_failover_replica_20260902.sql contains Leila's record in failover but not primary, alongside near-name decoys. Scope and exact identity links matter.
- service_events_ap_south_20260915.log spreads identities and results across shared trace IDs and includes unrelated queue/DNS/runtime noise. Preserve entire traces; distinguish concrete readback from operation success claims.
- service_resource_export_20260915_114455.json has per-record observed_at, explicit profile 404s, null identifiers, disabled connectors, blocked restores and retained security entries. Anonymous/absent resources need persistent resource-ID linkage; no direct identifier may remain.
- customer_data_snapshot_bundle_20260915.json shows one stable-reference-only tombstone and one with exposed name/email/phone/hash. A permitted stable reference must survive redaction.
- support_replica.log links historical email to support_002 through started/completed query context, then a missing marker. Similar names or neighboring rows alone do not establish ownership.
- PDFs are ordinary customer statements, support attachment, retention register and security journal. Extraction splits some timestamps across table cells; visual review prevents misreading them. A retention date is a policy fact, not a universal retention verdict.
- Screenshots are normal consoles: historical identities, decoy search hits, continuous connector, export availability, archive metadata, retained references, marketing identifiers and shared support. Healthy badges, encryption and intact checksums do not establish deletion compliance.

## Complete participant evidence review

- **Request meaning and time:** `deletion_requests.csv` contains 518 requests, including six languages, explicit non-deletion actions, repeated subjects at different `audit_at` cutoffs, and uppercase identifiers. `reported_status` and `reported_at` are workflow claims, not proof. Classify request meaning from the text and never infer a case class from the case number.
- **Identity:** `user_identities.csv` contains 850 stable user IDs and repeated names; `user_audit_log.csv` records historical email, phone and hash changes. Use exact stable IDs and time-valid alias edges. Do not merge by display name, numeric suffix, partial hash, or future alias. Some display strings contain U+FFFD replacement characters.
- **Activity log:** all 4,011 records were reconstructed and compared field-for-field against the CSV with zero mismatches. Its final 12 resource-identity links are appended after earlier activity and are not chronologically ordered; there are ten adjacent timestamp reversals in the last 12 records. Activity details show that `CHECK_DATA_FLOW/SUCCESS` means the flow remains enabled and `CHECK_RESTORE_ACCESS/SUCCESS` means a backup remains restorable. `activity_3435` explicitly targets `analytics_9914` for deletion.
- **Database snapshots:** 22 SQL files cover dated inventory, read-replica, failover, regional and reporting views. Preserve database, region, table and capture scope: an account may appear in a read replica but not primary. The regional snapshots include U+FFFD-corrupted names, restorable backups, disabled connectors, legal holds, and cross-store rows whose null or mismatched identifiers require external linkage.
- **Service logs:** 24 logs use different envelope formats and trace semantics. Join start and completion events by trace/resource, preserve full context, and distinguish a policy decision from a final readback. Some captures explicitly lack export-completion markers or report dropped events; absence in those files cannot prove system-wide deletion. Examples include the June 8 US-West cloud export, March 25 AP-Southeast archive, and August 24 US-East archive.
- **JSON evidence:** 24 records/snapshot files have independent export, capture and record timestamps. Some contain later observations than their top-level export time. They include identity-linked rows, null-field anonymized records, backups with restore permissions, connector configurations, export availability, search documents, support messages, audit rows, and legal holds. Preserve parent scope and the exact nulls; record presence is not disproved by missing subject fields.

The review receipts are organized by format in [`research/review-completion/`](research/review-completion/). They preserve source SHA-256 values, complete line coverage, normalized checkout equivalence, and file-level findings without copying raw contact details into this summary.

## Reuse and gaps

The S2 contract/preflight/evaluator/tests are installed in the existing official checkout. S3/S4 remain referenced source assets instead of competing solver copies. Report templates are explicitly unmeasured. Research and sample-label artifacts remain outside the submitted implementation tree.

Outstanding: schema-specific adapters; implementation of temporal identity and replica-aware state reduction; grounded category/condition tests; absence-scope handling; multilingual intent; provider/budget/access; usage accounting; independent reasoning fixtures; full target run; clean reproduction; portal details. No inference provider/model or package lock is selected yet.
