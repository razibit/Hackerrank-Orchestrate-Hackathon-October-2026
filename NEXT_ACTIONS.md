# Immediate actions

**Coverage gate: closed. Solver implementation has not started.** The review ledger is complete and all 74 unique participant evidence files have file-level receipts. See [coverage report](research/review-completion/coverage-report.md).

## First implementation slice

1. Confirm the authenticated challenge portal’s submission and interview windows before scheduling the final run. Keep this separate from per-request `audit_at` cutoffs, which are already present in the dataset.
2. Implement the smallest general vertical slice in the official checkout: strict input/output types, request-intent authorization, evidence manifest loading, stable subject resolution with time-valid aliases, and a scoped read-only evidence query interface. Do not hardcode case IDs or verdicts.
3. Add an as-of state reducer that distinguishes event time, observed time, source availability, snapshot scope, primary/replica identity, claims, and concrete readbacks. Retain unresolved state when evidence scope is incomplete.
4. Add deterministic policy selection and canonical operation ordering; validate every cited ID’s time and relevance. Write one row per request atomically and refuse fabricated `COMPLETE` outcomes.
5. Validate against independent synthetic cases first, including non-deletion requests, multilingual negation, future aliases, primary/replica conflicts, successful-but-risky connector/restore checks, and incomplete log captures. Then run the official sample evaluator and diagnose each mismatch.

Immediate implementation output: a general vertical slice that processes independent fixtures without case-specific rules and emits schema-valid rows whose status is supported by scoped evidence. Acceptance details are in [roadmap](IMPLEMENTATION_ROADMAP.md), [testing strategy](TESTING_STRATEGY.md), and [traceability map](REQUIREMENTS_TRACEABILITY.md).

Preparation checks from the earlier validation run:

```powershell
Set-Location -LiteralPath 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26'
python -B code/tools/preflight.py
python -B -m unittest discover -s code/tests -v
```

The current `code/main.py` and `code/evaluation/main.py` are empty. Do not describe the solver as implemented until the new vertical slice and its tests run successfully.
