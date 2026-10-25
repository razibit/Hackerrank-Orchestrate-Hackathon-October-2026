# Agent 1 read-only audit: v10 category blockers

Audit time: 2026-10-25 16:21 +06:00  
Run key: 61a7f1c04aa9f06477bdb187a551c10c632673d46a77a244f2aaf148137db957  
Scope: only cases 08, 12, 17, 18, 19, 21, and 29 from the run’s unresolved-cases file.

I read the participant evidence, extraction cache, selected v10 response-cache entries, the current extractor, and the evidence-classification prompt. I did not run inference or tests, change live source, open sample_output.csv, or use labels. I did not read or modify output/checkpoint contents. A prior filename-only listing of the run directory showed a few checkpoint names; I did not open them and made no further checkpoint access.

## Findings by case

| Case | Evidence that triggered a category blocker | Cause |
|---|---|---|
| 08 | evidence_27, page 2 line 5, order ORD-20264118 | Genuine policy-category insufficiency |
| 12 | evidence_27, page 2 line 7, order ORD-20264207 | Genuine policy-category insufficiency |
| 17 | evidence_27, page 2 line 9, order ORD-20264319; also evidence_01 profile-lookup trace, lines 16–21 | Genuine insufficiency plus extraction/provenance failure |
| 18 | evidence_94 search trace, lines 52–53 | Extraction/provenance failure on the start event |
| 19 | evidence_01 support, search, security, and profile-lookup traces, lines 11–15, 36–44, and 70–72 | Extraction/provenance failure plus prompt/category ambiguity |
| 21 | evidence_27, page 2 line 11, order ORD-20264402 | Genuine policy-category insufficiency |
| 29 | evidence_27, page 2 line 15, order ORD-20264600 | Genuine policy-category insufficiency |

### Cases 08, 12, 17, 21, and 29: the supplied policy does not cover the register rows

The participant PDF is titled “Disputed Orders and Tax Records Register.” Page 1 says rows carry an invoice date, finance owner, retain-until date, and case/reference number. The cited page 2 rows are dispute, chargeback, invoice-inquiry, and tax records with future retention-until dates; none states that a legal hold is active.

The extracted observations are correctly typed as RETENTION_REGISTER_ENTRY with category UNRESOLVED, state PRESENT, and snapshot proof. The v10 response reasons for the five rows also say that the entry does not match a supplied category. The supplied rules define SECURITY_AUDIT_LOG retention and LEGAL_HOLD_RECORD with an active-hold condition, but have no finance/disputed-order category. A future retention date does not establish an active legal hold. These five rows are genuinely unresolvable from the supplied category policy; keeping them blocked is correct.

Response-cache prefixes checked: 08 cca3ba794d6f; 12 08c3dc09aa73; 17 b411951c6e1f; 21 501655666d5e; 29 472b7879996c.

### Cases 17, 18, and 19: trace fields lose their line-level provenance

In code/audit_agent/extractors.py, _log_source collects every non-empty field from each trace at line 530, then seeds every line’s fields from that trace at line 566 before overlaying the current line. That copies facts from sibling events into an observation whose raw_text is only the current source line. The classification prompt says to classify each observation independently and use only facts in that observation. The merged fields therefore violate the prompt’s evidence boundary.

Concrete effects in the cached extraction:

- Case 17, evidence_01 line 16 is profile_lookup_started. Its source line has no resource ID or rows/status result. The completed lookup is line 21 with account_4092, rows=0, and HTTP 404. The extracted start and connection/retry/recovery lines inherit the resource and 404 result; the model marks those observations ABSENT but leaves their category UNRESOLVED. This is result and resource provenance copied backward across the trace.
- Case 18, evidence_94 line 52 is index_query_started; its raw line has only the resource ID and lookup key. The extracted fields also contain result=hit, total_hits=1, and the email that appear in line 53’s index_query_completed result. The model response for the start line still returns category UNRESOLVED and state UNKNOWN, while line 53 is classified SEARCH_INDEX_ENTRY/PRESENT. The completion is the supported result; the start line should not independently become a material data candidate.
- Case 19, evidence_01 lines 12–14 are connection_acquired, dependency_retry, and dependency_recovered. Their raw lines have no support resource or matched identifier; extracted fields inherit those values from the related message scan on line 15. The model consequently returns UNRESOLVED categories for these operational lines. Similarly, line 42’s security connection event inherits audit resource/row context from the same trace’s query/readback, and line 70’s profile_lookup_started event inherits rows=0/404 from the completion at line 72. These are not separate stored records.

The profile-log outputs also show category ambiguity: the account_9102 completion is classified USER_PROFILE/ABSENT in one cached response, while a related lookup-log observation for that resource is UNRESOLVED in another. The prompt describes USER_PROFILE as an account/customer profile record but does not explicitly say that a completed profile lookup is evidence about the target profile rather than a claim that the log artifact itself is a profile record.

### Case 19 search result: the target category is underspecified

Evidence_01 line 36 is an explicit index_query_completed event with result=hit and a subject correlation key. Its cached classification returns UNRESOLVED because the model treats it as a query event, not a stored index entry. In the same v10 run, evidence_94 line 53 is an index_query_completed event with result=hit and total_hits=1 and is classified SEARCH_INDEX_ENTRY/PRESENT. The current prompt defines SEARCH_INDEX_ENTRY as a user-linked index document but does not state when a completed, subject-linked query result is sufficient evidence for that target category. This is a prompt/category ambiguity; make one evidence rule and apply it consistently.

The support scan on evidence_01 line 15 is categorized SUPPORT_MESSAGE, but its conditional shared-context policy remains UNRESOLVED because the log has no conversation content. That unresolved policy fact is correct and should remain unresolved; do not infer conversation context from a scan event.

## General corrections for review

1. Keep each parsed log row’s fields and provenance local to that row. A trace ID may relate rows, but must not copy resource IDs, row counts, status codes, results, or identifiers from a sibling line. If trace-level aggregation is needed, represent it separately with the exact source locators for every constituent fact. Never let a later completion result appear on an earlier start event.
2. Do not promote generic lifecycle rows such as connection_acquired, dependency_retry, or dependency_recovered to independent data-resource candidates solely because a sibling row in the trace identifies a user or resource. Preserve these as supporting activity evidence. Use the explicit, time-valid completed readback as the state-bearing observation.
3. Clarify category referents in the prompt. A completed profile_lookup with scoped rows=0/HTTP 404 can establish USER_PROFILE/ABSENT for that lookup scope; a start/connection/retry row cannot borrow that outcome. A completed, subject-linked index_query with an explicit hit can be SEARCH_INDEX_ENTRY/PRESENT if the query result is the direct readback; a start event alone proves neither a hit nor a stored entry. A zero-result query must remain scoped and must not imply global absence without complete-scope evidence.
4. Keep the finance register entries UNRESOLVED unless the official supplied policy adds an applicable category and condition. Do not relabel them as legal holds based only on the retention date or document title.

## Regression examples to add when implementation is authorized

- Plain finance/disputed-order register row with subject reference and future retain-until, but no hold status: retain UNRESOLVED/PRESENT/snapshot. Same row with explicit active hold: LEGAL_HOLD_RECORD with the active condition; explicitly inactive hold must not become active.
- One trace containing profile_lookup_started, connection_acquired, and profile_lookup_completed with resource ID, rows=0, and HTTP 404: only the completion carries those result fields; it supports scoped USER_PROFILE/ABSENT. Earlier lines retain their own fields and do not become separate material records. Move completion past audit_at and verify it cannot leak into an earlier event.
- One trace containing index_query_started followed by index_query_completed result=hit and total_hits=1: only completion carries the hit and supports SEARCH_INDEX_ENTRY/PRESENT. Start-only evidence stays UNKNOWN. A zero-hit result must not prove absence outside its explicit scope.
- Support-message and security-audit traces with connection/retry/recovery events: generic lifecycle rows do not inherit message identifiers or audit row counts and do not independently fail category resolution. The explicit message scan can establish its own supported category, while its content-dependent policy condition stays UNRESOLVED without message content.
- Completed audit-record readback with an adjacent connection_acquired row: the typed readback carries SECURITY_AUDIT_LOG and its own rows/scope; the connection event does not.