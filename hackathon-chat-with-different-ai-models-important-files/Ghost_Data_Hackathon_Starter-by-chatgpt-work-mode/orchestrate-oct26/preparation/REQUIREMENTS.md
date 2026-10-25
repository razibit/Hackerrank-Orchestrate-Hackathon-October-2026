# Requirements and engineering checklist

Source snapshot: interviewstreet/hackerrank-orchestrate-october26, commit acb3dfca6e94e4803a26e72c49074a488de93c93, inspected 24 October 2026. Live challenge page also read.

| Requirement | Implementation / acceptance check |
|---|---|
| 518 target requests | Exactly one root output.csv row per target case_id; lexical case_id order |
| 32 labeled samples | Separate inference and evaluation; never read labels in prediction path |
| Deletion intent first | COMPLETE / INCOMPLETE only for authorized deletion; otherwise NOT_APPLICABLE, [] |
| Current/historical identity | Link request email to stable user via snapshot and audit history; preserve provenance and temporal validity |
| Time bound | Filter files by captured_at and internal observations/events by their own time; never use information after audit_at |
| Claims versus state | Workflow COMPLETE / operation SUCCESS is not sufficient proof |
| Full evidence discovery | Search all relevant identifiers and grounded resource links across 94 mixed-format files and global activity |
| Deletion policy | Load all 15 rules; handle DELETE, REDACT, ANONYMIZE, RETAIN and tombstone special case |
| Recreated data | Discover active sync/import/restore paths; disable flows/block restore before dependent record changes |
| Output | Exact header case_id,deletion_status,steps_json; each step has exactly seven required fields |
| Evidence IDs | Findings and COMPLETE verification cite actual file/activity/audit IDs at or before cutoff |
| Future plan | INCOMPLETE remediation and verification use empty evidence_id |
| Ordering | Phase, published operation rank, system_id, resource_id; renumber after sorting |
| Evaluation | Status, step, field and sequence metrics; >=3 participant-created cases; failures and improvements |
| Cost accounting | Final run provider/model/calls/tokens/cost, per model and overall, average over 518 |
| Packaging | README + code + Markdown evaluation reports; no dataset, environments, caches, secrets or nested archives |
| Transcript | Root log.txt in chat_transcript slot; preserve complete structured traces separately |

## Policy map read directly from deletion_rules.csv

- DELETE: USER_PROFILE, SECONDARY_IDENTIFIER, SEARCH_INDEX_ENTRY, CACHE_ENTRY, USER_EXPORT, MARKETING_PROFILE; SUPPORT_ATTACHMENT when it belongs only to subject.
- REDACT: shared-context SUPPORT_MESSAGE; EMAIL_DELIVERY_LOG containing email; ACCOUNT_TOMBSTONE retaining only permitted stable reference.
- ANONYMIZE: attributable ANALYTICS_PROFILE and PRODUCT_TELEMETRY.
- RETAIN: SECURITY_AUDIT_LOG within supplied retention; active LEGAL_HOLD_RECORD; BACKUP_ARCHIVE where restore access can be blocked. Backup retention still requires preventing prohibited restoration.
- Where a supplied condition is not established, investigate; do not silently generalize a conditional rule.

## Important distinctions and documentation gaps

- README places evaluation files under code/evaluation/; problem_statement/AGENTS use evaluation/ shorthand. Use code/evaluation/ in the source tree and package README + code, as README explicitly instructs.
- agent_trace_instructions.md separately requests agent-trace.zip. Live page/README specify log.txt in the chat_transcript slot. Prepare BOTH; keep trace ZIP separate from code.zip and use only a supported additional upload channel. Do not replace log.txt or nest the trace ZIP inside code.zip. Ask organizers if no additional trace slot exists.
- AGENTS.md's submission URL has a four-w 'wwww' typo. Use the working three-w URL supplied by the user and verified in the live browser; do not propagate the typo into commands.
- AGENTS.md discusses dependency-aware downstream-first remediation; problem statement requires exact operation/system/resource sorting. Discover safe dependencies internally and serialize to the explicit canonical order. If genuine dependency constraints conflict within that order, retain the case and seek organizer clarification; do not invent custom fields or ordering.
- The repository has no fixed deadline configured. Live page displayed a 22:53:40 submission countdown when inspected; interview endpoint shown as 26 October 2026 06:30 AM +06. Verify the live countdown; do not assume an interview window extends submission time.
- This hosted session exposes no authoritative exact runtime model ID. log.txt records that limitation instead of fabricating one. Future local sessions should read model from their own authoritative rollout metadata. A summarized log is not the same as a raw trace.
