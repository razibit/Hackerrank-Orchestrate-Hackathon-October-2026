# Proposal: deterministic legal-hold condition guard

Owner: Agent 0 integration / Agent 3 policy review. This is a proposal only; Agent 4 did not modify `engine.py` or `policy.py`.

In the assigned snapshot, `engine._explicit_policy_condition()` has deterministic branches for `SECURITY_AUDIT_LOG`, `BACKUP_ARCHIVE`, and `ACCOUNT_TOMBSTONE`, then returns `None` for other categories. For `LEGAL_HOLD_RECORD`, that leaves the condition supplied by the model as decisive after the category is chosen.

Consider adding a `LEGAL_HOLD_RECORD` branch that accepts only verified hold-specific fields from the participant-facing evidence schema. Explicit active status may resolve to `TRUE`; explicit released/inactive status may resolve to `FALSE`; missing, conflicting, or ambiguous hold state should resolve to `UNRESOLVED`. A row state of `PRESENT` or a future `retention_until` value alone must never resolve an active legal hold. Verify the exact field allowlist against the supplied evidence before implementation. If the evidence does not establish that a record is a legal-hold record, keep category classification unresolved or use its actual supported category.

This would make the user-reported false-positive guard deterministic while preserving the distinction between an ordinary retention obligation and a genuinely active legal hold. The prompt update in this candidate is useful independently but cannot guarantee model compliance; no live model measurement was made.