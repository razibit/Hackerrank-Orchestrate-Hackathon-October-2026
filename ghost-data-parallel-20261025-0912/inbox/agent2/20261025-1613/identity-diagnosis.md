# Read-only v10 identity-link diagnosis

Reviewed: 2026-10-25 16:13 +06:00

## Scope and sources

Read only the six named rows in participant-facing `sample_deletion_requests.csv`, `user_identities.csv`, `user_audit_log.csv`, the current live identity resolver and candidate index, and the v10 extraction cache at `.cache/sample_v10/extract/591218c3d8466898d72aa48d1f699b0d21fb3b98f4cd29aa13ba85f92c430cc1/`. The cache fingerprint matched the current dataset. It held 4,197 source observations and 4,011 activity observations. I did not open `sample_output.csv`, read `.run` checkpoints or `output.csv`, rerun extraction, run inference, or change source.

## Findings

| Case | Identity mapping | Cached exact subject link at `audit_at` | Diagnosis |
|---|---|---|---|
| `case_05` | Unique | Yes: `evidence_54`, `table:customer_profiles_failover_replica:row:1`, exact `user_id`, email, and phone; observed and available 2026-09-02, before the 2026-09-08 cutoff. | Not an identity-link miss. Candidate index also returns the matching account resource's activity row; that activity is a claim, not proof of deletion state. |
| `case_16` | Unique | Yes: `evidence_05` rows 15, 23, 1, 16, and 24 contain exact `subject_reference`/`customer_reference` and/or email/phone links across the primary, read-replica, search, and security observations. All were observed and available at 2026-09-21 10:00, exactly the inclusive cutoff. | Not an identity-link miss. Five direct observations support the link; the candidate index returns six including a same-resource peer. |
| `case_24` | Unique | Yes: `evidence_27`, `page:2:line:13`, has an exact `subject_reference`; `evidence_92` has exact email links in account profile and search observations. Those observations were available by the 2026-09-15 12:00 cutoff. | Not an identity-link miss. The cache also contains eight exact-identifier field hits in `evidence_02`, but their availability is 2026-09-17, after the cutoff, so they are correctly excluded. Earlier valid links remain. |
| `case_01` | Unique | No: zero exact stable-ID or email/phone/hash field hits, zero exact email/hash text-token hits, and zero time-valid phone mentions in cached raw text. | Identity itself is resolved; subject-linked evidence is insufficient in this extraction cache. |
| `case_02` | Unique | No: zero exact stable-ID or email/phone/hash field hits, zero exact email/hash text-token hits, and zero time-valid phone mentions in cached raw text. | Identity itself is resolved; subject-linked evidence is insufficient in this extraction cache. |
| `case_04` | Unique | No: zero exact stable-ID or email/phone/hash field hits, zero exact email/hash text-token hits, and zero time-valid phone mentions in cached raw text. | Identity itself is resolved; subject-linked evidence is insufficient in this extraction cache. |

For `case_05`, `case_16`, and `case_24`, every direct candidate hit passed `matches_for_evidence`; none was rejected for reassigned or overlapping ownership. Their unresolved result therefore is downstream of identity resolution and candidate retrieval, based on the current code/cache. The direct links establish subject attribution only; they do not prove deletion completion or record treatment.

For `case_01`, `case_02`, and `case_04`, the cache does not establish an ambiguous identity: request emails resolve uniquely. It also supplies no exact subject link. This is genuine evidence insufficiency within the current extraction cache, not proof that original evidence files contain no identifier; an unextracted identifier in a source artifact remains possible and was not checked by rerunning or manually re-extracting sources.

## General rules and synthetic regression proposals

- A unique exact stable ID or normalized email, phone, or hash match is a deterministic subject link only when its ownership interval covers the observation time and both observation and availability times are at or before `audit_at`.
- Keep conflicting stable IDs, overlapping active aliases, and reassigned aliases unresolved. Do not join by names, weak similarity, resource prefixes, or array position.
- Treat activity/status claims as claims; a subject link does not establish deletion state.

Suggested synthetic regressions: a unique exact stable-ID link passes; an exact historical alias links only during its proven interval; a reused alias is rejected for the previous owner after reassignment; evidence captured after `audit_at` is excluded even when it contains the exact identifier; and same-name/resource-prefix-only evidence remains unresolved. No tests were run for this read-only diagnosis.