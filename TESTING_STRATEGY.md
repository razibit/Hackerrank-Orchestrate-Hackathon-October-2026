# Testing and evaluation

## Already executed

[Verification record](research/VERIFICATION.md): six contract tests pass; preflight validates published counts, manifest paths and public sample structure. All 94 evidence files structurally parse/decode; 11 PNGs/seven PDF pages visually inspected. Five reference probes expose five defects. Comparator self/mutation checks test mechanics, **not agent accuracy**. No actual audit pipeline has run.

Coverage is complete, but tests must preserve corpus-specific semantics discovered during review: retain all activity rows and order by their event timestamps rather than physical CSV position; distinguish export time from capture/observation/record time; keep each SQL database, replica, and region scoped; and treat absent log completion markers or dropped auxiliary events as incomplete evidence. A `SUCCESS` label on a connector check or restore check is not proof that data is safely gone.

## Required tests

| Layer | Cases | Acceptance |
|---|---|---|
| Intent | Deletion, prior-deletion verification, English/Bengali/Japanese negation, access/correction/export/opt-out, hostile text mixed with valid request | Meaning controls authorization; embedded instructions cannot alter policy |
| Identity | Old/current email/hash, phone formats, same-name decoy, reused alias, future snapshot/change | Stable-subject provenance; no future leakage or weak-name-only join |
| Extraction | All JSON shapes/parent context, full log trace correlation, split PDF timestamps, all screenshots/SQL scopes | Correct located facts; no silent dropped files; null is not record absence |
| Temporal | Equal cutoff, microsecond later, offsets, file capture vs observation, primary/replica conflict | Later facts excluded, equality allowed, physical scopes preserved |
| Policy | All 15 categories; conditional true/false/unknown; contact identity vs analytics profile; message vs attachment | Content-grounded rule; unknown never defaults DELETE |
| Tombstones | Stable reference only; residual name/email/phone/hash/nested identifiers | Keep allowed reference; redact prohibited fields; anonymized analytics cannot remain attributable |
| Absence | Explicit 404/zero-row, exhaustive snapshot_scope, partial omission, query failure, wrong subject | Only scoped positive proof supports absence |
| Recreation | Enabled sync despite SUCCESS, disabled connector, eligible restore, deletion block | Actual config/readback determines risk |
| Planner | Violations plus compliant account/security; duplicates; ordering ties | Complete required verification set; canonical order; no duplicate actions |
| Model failures | Timeout/429, malformed JSON, invented but schema-valid citation, retry/budget exhaustion | Bounded retries/tools/calls; visible unresolved state and accounted usage |
| Output | Missing/extra/duplicate cases, bool/float numbering, nonobject steps, wrong fields/state, empty/late proof | Actionable validation errors; no silent acceptance/crash |
| Reproduction | Fixed facts vs fresh extraction; cold/warm cache; changed config/data on resume | Fixed facts yield identical bytes; cache/checkpoint invalidation; variance disclosed |

## Independent end-to-end cases

At least three must run through the real agent, with exact seven-field expected steps and observed results written in Markdown:

1. Data-copy request explicitly forbids deletion; exposed profile remains. Expect NOT_APPLICABLE/[] in English and Bengali.
2. Historical alias with absent primary, remaining replica/search and active connector. Expect INCOMPLETE, grounded findings, disable-before-treatment and required final checks.
3. Scoped compliant tombstone, retained security, absent profile, disabled flow and blocked restore. Expect COMPLETE with only cited pre-cutoff verification. Add exposed-hash variant requiring redaction.
4. Pre-cutoff presence vs post-cutoff deletion. Expect INCOMPLETE without future evidence.
5. Analytics-system contact identifier vs actual analytics profile. Expect DELETE vs ANONYMIZE based on category, not prefix.

[Copied fixture brief](hackerrank-orchestrate-october26/code/evaluation/SYNTHETIC_CASES.md) contains proposals, not executed reasoning tests.

## Metrics and isolation

Inference must not open sample_output.csv. Generate separate predictions, then evaluate 32 labels. Report status accuracy; joint exact-row match (status + entire ordered steps); exact seven-field multiset step precision/recall/F1; seven-field positional accuracy with missing/extra positions wrong; exact sequence match; structural-order compliance separately. Include confusion matrix and per-operation/category/citation errors when useful. Target labels are hidden: no target accuracy claim.

Installed S2 comparator validates exact coverage first and reports status, exact-step precision/recall, seven-field positional accuracy and exact sequences. Add F1/joint row metric before final reporting. S3 omits step_no from signatures, ignores extras and collapses duplicate IDs during dict load; do not mix incomparable percentages.

## Packaging

Extract eventual code.zip into a fresh temporary directory, supply dataset separately and follow README. Audit [ZIP members](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.infolist) for traversal, data, environments, credentials and nested archives. Include actual root dependencies/config if required; README's example command only names README+code. Keep trace ZIP separate.
