# Agent 3 policy review — staged candidate

## What changed

- `code/audit_agent/policy.py` now maps false conditional outcomes explicitly to the safe result supported by the supplied rule. It also checks that each rule's action matches the expected false-condition interpretation; mismatches fail closed. A false backup condition is compliant only when the archive is absent or already blocked; an active unblocked archive remains an error.
- `code/audit_agent/policy_conditions.py` adds deterministic structured resolvers for the conditional rules that need evidence checks:
  - Legal hold is active only when a specific hold status/flag says so. A present row, resource name, or future retention deadline returns `UNRESOLVED`.
  - Security-log retention uses the supplied `retention_until` deadline at `audit_at`; generic legal-retention fields do not qualify.
  - Support-message condition resolution requires actual message/context content. If absent, it returns `UNRESOLVED`; semantic classification is still needed when content exists.
  - Backup retention requires explicit blocking capability or a direct `deletion_block` control. Restore permission/eligibility alone is not proof of blocking ability.
  - Account tombstones require a deleted status and a stable reference; the shape check requires name, email, phone, and email hash to be empty and all recognized stable references to equal the subject's stable ID.
- `code/tests/test_agent3_policy.py` adds seven independent synthetic tests for the requested cases and remediation ordering.
- `code/prompts/agent_system_guidance.md` preserves the user's reusable challenge guidance as persistent prompt documentation, not as a fabricated chat turn. `code/prompts/agent3_policy_assignment.md` is an exact copy of the attached task prompt.

## Confirmed live-engine issue and integration boundary

The live `engine.py` is byte-identical to Agent 3's isolated snapshot. Its current `_explicit_policy_condition` has no `LEGAL_HOLD_RECORD` branch and returns `None`, so a model-supplied `TRUE` can survive even when structured evidence contains only `record_state=PRESENT` and a future retention date. The current security-log branch also accepts generic aliases such as `retained_until`, and missing dates return `None`, which leaves a model result in place. These are resolver/integration defects, not evidence that any particular request qualifies for retention.

The helper is staged but is not wired into `engine.py`, because Agent 3 is explicitly barred from editing that file. See `engine-integration-proposal.md` for the exact adapter proposal. Agent 0 must add the new module and test/prompt paths to the explicit `SUBMISSION_MANIFEST.md` allowlist if it accepts them.

## Missing evidence versus resolver defects

- **Resolver defect confirmed:** the live engine permits a model condition to stand when deterministic evidence is absent for a legal hold; it also treats `retained_until` as a security-log deadline.
- **Genuinely missing evidence:** without explicit active-hold status, a supplied security `retention_until`, support-message content, or restore-block capability, the relevant condition remains unresolved. The run should remain blocked until source evidence resolves it; tests do not invent an outcome.
- No organizer labels, case-family rules, target answers, or Foundry calls were used.

## Remediation-order review

The current planner separates FINDING, REMEDIATION, and VERIFICATION, sorts by the contract's operation rank, places `DISABLE_DATA_FLOW` and `BLOCK_RESTORE` before record changes, preserves `RETAIN` records as verification, and clears evidence IDs from all future verification steps in an incomplete plan. The synthetic test verifies those properties.

One gap remains: the planner then sorts record changes by `system_id` and `resource_id`; it does not order downstream copies before source records when a grounded dependency requires that. Agent 0 should preserve the contract's operation rank and add a dependency-aware order among steps of the same operation rank only when source evidence establishes an edge. If an evidenced dependency conflicts with the canonical operation order, surface that for a contract decision rather than silently changing the required sort. This patch does not modify the planner.

## Test results

Python executable: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe`

Environment:
- `PYTHONPATH=D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent3\code`
- `GHOST_DATASET_PATH=D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\dataset`

Targeted command:
```powershell
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent3\code\tests' -p 'test_agent3_*.py' -v
```

Result: **7 tests passed** (0.003s). Exact output: `test-agent3-output.txt`.

Full-suite command:
```powershell
& 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent3\code\tests' -v
```

Result: **77 tests passed** (0.100s). Exact output: `full-suite-output.txt`.

No sample evaluation or target rerun was performed; the helper is not integrated into the live engine.
