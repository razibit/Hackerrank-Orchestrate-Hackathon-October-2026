# Agent 2 Identity and Temporal Evidence Change

## Candidate files

- `code/audit_agent/identity.py`
- `code/tests/test_agent2_identity.py`

`code/audit_agent/data.py` is unchanged. The reviewed ISO `Z` and numeric-offset timestamps compare as instants, while malformed and timezone-naive timestamps fail closed; no parser edit was justified by these checks.

## Changes

- An audit row's `old_value` no longer creates a second interval starting at an unknown lower bound when the immediately preceding event already set that same normalized value. The preceding `new_value` interval already ends at the current event time. This prevents that alias from appearing active before the known assignment and falsely making a historical owner ambiguous.
- `resolve` rejects a request timestamp after `audit_at`. `matches_as_of` and `matches_for_evidence` reject event or observation timestamps after their evidence cutoff.
- Eight new synthetic tests cover historical aliases, reassignment and interval boundaries, overlapping owners, missing or malformed event times, timezone offsets, future cutoffs, and duplicate names.

## Measured checks

A read-only diagnostic used only `deletion_requests.csv`, `user_identities.csv`, and `user_audit_log.csv` from the participant dataset. It resolved 518/518 request emails, found 0 unresolved identities, 0 requests later than `audit_at`, and 0 cases where a returned alias lacked evidence available by that case's cutoff. Four audit transitions in the supplied identity history repeat the immediately preceding `new_value` as `old_value`; no case IDs or labels were used to encode behavior.

The diagnostic measures identity resolution only. Agent 0's latest published status did not include a final unresolved list, so this work does not claim that every case has subject-linked deletion evidence or improves end-to-end target accuracy. No prediction run, sample evaluation, or model call was made. Partial snapshot handling was unchanged; its existing regression passed in the full unit suite.

## Exact test commands and results

Focused invocation initially attempted:

```powershell
$env:PYTHONPATH='D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent2\code'; & 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest code.tests.test_agent2_identity -v
```

Result: failed with `AttributeError: module 'code' has no attribute 'tests'` because `code` resolved to Python's standard-library module. The corrected discovery command passed:

```powershell
$env:PYTHONPATH='D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent2\code'; & 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -p test_agent2_identity.py -v
Ran 8 tests in 0.001s — OK
```

The complete unit suite passed with the read-only participant dataset configured:

```powershell
$env:PYTHONPATH='D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent2\code'; $env:GHOST_DATASET_PATH='D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\dataset'; & 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe' -B -m unittest discover -s code\tests -v
Ran 78 tests in 0.072s — OK
```

`code/tests` contains no `sample_output.csv` reference. The full suite passed `test_incomplete_snapshot_does_not_prove_absence` and `test_future_observation_is_excluded`.

## Integration note

`code/SUBMISSION_MANIFEST.md` does not currently list `code/tests/test_agent2_identity.py`. Agent 0 can decide whether to add that regression file to the package allowlist during integration; this candidate does not modify the manifest or any other owner's files.