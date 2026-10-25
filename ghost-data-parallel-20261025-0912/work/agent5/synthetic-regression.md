# Legal-hold synthetic regression

These are general policy fixtures, independent of any dataset case or answer label.

## Negative control

- Category: `LEGAL_HOLD_RECORD`
- Evidence: `record_state=PRESENT`, `retention_until` later than `audit_at`
- Evidence does not state that a legal hold is active.
- Expected condition: `UNRESOLVED` (or `FALSE` if the source explicitly proves there is no hold).
- Expected policy result: do not apply `RETAIN`; do not report `VERIFY_RECORD_PRESENT` as a required retention check based only on those fields.

## Positive control

- Category: `LEGAL_HOLD_RECORD`
- Evidence explicitly states the hold is active, identifies the subject/resource, and is available by `audit_at`.
- Expected condition: `TRUE`; apply the supplied `RETAIN` rule to that scoped record.

## Executed Agent 5 test

`test_agent5_legal_hold.py` supplies the negative fixture to the actual deterministic `_explicit_policy_condition` function. It verifies that row presence plus a future date returns no condition and that unresolved policy raises `PolicyResolutionError`; an explicit `TRUE` condition follows the retain action.

This regression does not invoke the runtime model or validate its prompt fallback. That owner must add the same fixture to the prompt/parser/model regression suite before integration.
