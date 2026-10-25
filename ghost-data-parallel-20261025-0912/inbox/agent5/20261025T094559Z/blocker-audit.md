# Read-only v9 blocker-family audit

Source: Agent 0 final unresolved_cases.txt (294 lines), participant-facing policy/evidence rules, and the isolated source snapshot. No per-case checkpoints/caches, organizer truth, or sample answers were opened for this audit. Counts below are first-stopping reasons; they are not mutually complete root-cause counts after earlier blockers are repaired.

## Families and triage

| First-stopping reason | Cases | Triage |
|---|---:|---|
| SECURITY_AUDIT_LOG conditional policy unresolved | 135 | Mixed. The rule needs a retention cutoff. The deterministic resolver reads five explicit date fields and parses three date formats. If a linked source has a date in an unrecognized field/format or extraction omitted it, that is a general extraction/resolution fix. If the applicable cutoff is absent, conflicting, or after the required evidence cutoff, the case must stay unresolved. |
| Candidate subject link unresolved | 68 | Mixed. A time-valid exact alias or stable subject reference present in cited source points to classification/retrieval work. If only names, weak similarity, or an unlinked workflow claim is available, the evidence is genuinely insufficient to join the subject. |
| SUPPORT_MESSAGE conditional policy unresolved | 27 | Mixed. The rule depends on message content/context. Recoverable body text already in the source points to extraction or model-reasoning work; missing or generic content correctly remains unresolved. |
| BACKUP_ARCHIVE restore-blockability unresolved | 25 | Mostly evidence-dependent. Explicit blockability/control evidence can resolve the condition. A restore-allowed value or an archive row alone does not prove blockability; if no explicit control evidence exists, keep blocked. |
| ACCOUNT_TOMBSTONE condition unresolved | 2 | Mixed, low volume. The deterministic resolver needs a deleted/tombstoned state and the permitted stable reference, or explicit evidence of a non-deleted state. Missing fields are a source gap; present but unrecognized fields are fixable. |
| Material evidence category unclassified | 4 | Likely extraction/classification work if supplied content is readable and fits an allowed category. If the source is unreadable or has no category-defining content, preserve uncertainty. |
| No subject-linked evidence supports a decision | 4 | Evidence-limited unless an exact historical/current identifier or stable-reference link was missed. Do not join by name or weak similarity. |
| No scoped state proof | 15 | Usually evidence-limited when the supplied capture is partial or lacks an explicit scoped readback. A missed complete readback is a retrieval fix; missing/partial scope is not evidence of absence. |
| Workflow claims only | 10 | Evidence-limited under the contract. A success status/operation claim is not proof; resolve only if another scoped source supports current state. |
| Flow/export state remains PRESENT without a grounded active/disabled state | 4 | Evidence-limited unless an explicit status field was present but missed. Row presence alone does not establish an active flow; preserve the block. |

These reason families sum to 294. The flow-related no-scoped-state case is counted under No scoped state proof, not again under the four PRESENT-only flow cases.

## Highest-value general fixes

1. Review the 135 retention cases for source date fields/values before changing semantics. Extend only general date-field/date-format support that participant evidence actually uses; keep missing/conflicting dates unresolved.
2. For the 68 subject-link cases, compare the classifier's unresolved candidate against exact time-valid aliases and stable IDs visible in the cited source. Improve extraction/routing only for those grounded links.
3. Narrow the SUPPORT_MESSAGE second pass to actual message text and keep generic/absent text unresolved.
4. Keep BACKUP_ARCHIVE distinctions: explicit can_block_restore/equivalent or configured-control evidence can resolve blockability; restore_allowed and row presence alone cannot.
5. Maintain the release block for workflow-only, partial-scope, and unlinked evidence. No missing rows or conclusions should be invented.

## Scope limitation

The final list gives one first-stopping reason per unresolved case but no source excerpts or evidence IDs. Therefore this audit distinguishes likely fix paths from hard evidence gaps by family; it cannot honestly claim a case-by-case count of fixable failures versus truly absent evidence without consulting the cited source records. Agent 0 retains the final integration decision.
