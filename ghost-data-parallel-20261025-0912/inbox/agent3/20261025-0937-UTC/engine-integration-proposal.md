# Agent 0 engine integration proposal

This proposal is intentionally separate from the candidate source because Agent 3 does not own `engine.py`.

## 1. Import the reviewed helper

Add alongside the policy imports:

```python
from .policy_conditions import (
    resolve_policy_condition_from_fields,
    tombstone_has_only_stable_reference,
)
```

## 2. Delegate deterministic policy-condition resolution

Update `_explicit_policy_condition` to accept the stable subject ID and delegate:

```python
def _explicit_policy_condition(
    observation: Observation,
    category: str,
    cutoff: datetime,
    stable_user_id: str,
) -> str | None:
    return resolve_policy_condition_from_fields(
        category,
        observation.fields,
        observation.state,
        cutoff,
        stable_user_id=stable_user_id,
        raw_text=observation.raw_text,
        source_kind=observation.source_kind,
    )
```

At the existing call in `_validate_classification`, pass `stable_user_id`:

```python
condition = _explicit_policy_condition(observation, category, cutoff, stable_user_id)
if condition is not None:
    classification = {**classification, "policy_condition": condition}
```

The helper deliberately returns `UNRESOLVED` (not `None`) when a targeted condition lacks required evidence. That value must override a model response so `required_treatment` fails closed. For SUPPORT_MESSAGE, content permits the validated semantic resolver; no content forces UNRESOLVED.

## 3. Tighten tombstone exposure override

Replace the current `_only_stable_identifier_tombstone(observation, stable_user_id)` check with:

```tombstone_has_only_stable_reference(observation.fields, stable_user_id)```

This preserves the existing gate on a deleted account while requiring the populated stable references to match the subject and checking recognized alternate direct identifiers.

## 4. Package allowlist and regression

If accepted, add these source/test/prompt paths to `code/SUBMISSION_MANIFEST.md`:
- `code/audit_agent/policy_conditions.py`
- `code/tests/test_agent3_policy.py`
- `code/prompts/agent_system_guidance.md` (reference documentation only; not an inference prompt)
- `code/prompts/agent3_policy_assignment.md` only if the attached role prompt should be part of the package rather than the challenge trace.

Then run the synthetic policy tests, full suite, and Agent 0's relevant sample diagnostics. Do not infer hidden-target effects from the synthetic fixtures.

## 5. Dependency ordering review

The current planner uses operation rank, then system/resource IDs. It does not consult grounded dependency edges when two destructive copies require the same operation. Preserve the contract's operation rank, then topologically order downstream before source among equal-rank steps only when the evidence proves the dependency. If a proven edge conflicts with the contract's canonical operation order, flag that conflict for Agent 0's contract review instead of silently changing the sort. Never infer dependencies from resource naming or case grouping.
