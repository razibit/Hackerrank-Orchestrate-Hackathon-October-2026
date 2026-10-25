# Assignments

- Agent 0: live checkout, active `.run/target_v9` target run, integration, final output/report/package, root logging.
- Agent 1: `code/audit_agent/extractors.py`; new extractor-only tests.
- Agent 2: `code/audit_agent/identity.py` and `code/audit_agent/data.py`; new temporal/identity-only tests.
- Agent 3: `code/audit_agent/policy.py`; new policy-only tests; propose engine changes to Agent 0.
- Agent 4: `code/audit_agent/model.py` and `code/prompts/*.md`; new model/parser-only tests; no Foundry calls without GPU lease.
- Agent 5: `code/evaluation/` and uniquely prefixed `code/tools/agent5_*.py`; independent evaluation and diagnostics only.
- Agent 6: coordination only; no source edits, no tests that mutate shared artifacts, and no inference.

Agent 0 is the sole integration and release authority. Source ownership applies within each isolated candidate copy; no two agents edit the same file in their own workspaces.
