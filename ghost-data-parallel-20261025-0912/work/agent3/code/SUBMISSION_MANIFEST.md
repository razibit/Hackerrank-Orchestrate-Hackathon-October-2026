# `code.zip` inclusion list

The archive is built explicitly from this allowlist. It contains source, prompts, tests, run/evaluation tools, setup instructions, and required reports only.

```text
code/.env.example
code/README.md
code/SUBMISSION_MANIFEST.md
code/requirements.txt
code/main.py
code/audit_agent/__init__.py
code/audit_agent/cache.py
code/audit_agent/data.py
code/audit_agent/engine.py
code/audit_agent/extractors.py
code/audit_agent/identity.py
code/audit_agent/model.py
code/audit_agent/policy.py
code/audit_agent/types.py
code/prompts/evidence_classification.md
code/prompts/intent_classification.md
code/prompts/policy_condition_resolution.md
code/tools/build_synthetic_cases.py
code/tools/contract.py
code/tools/evaluate.py
code/tools/preflight.py
code/tools/package_submission.py
code/tools/validate_output.py
code/tests/test_audit_agent.py
code/tests/test_contract.py
code/tests/test_extractors.py
code/tests/test_model.py
code/tests/test_preflight.py
code/evaluation/SYNTHETIC_CASES.md
code/evaluation/evaluation_report.md
code/evaluation/usage_report.md
```

Excluded: datasets and evidence, `sample_output.csv`, `.env`/`.env.local`, credentials, virtual environments, caches, generated predictions, run checkpoints, Python bytecode, and nested archives.
