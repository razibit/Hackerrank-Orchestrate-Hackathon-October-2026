# Agent 5 commands and results

Run from PowerShell. Dataset and prediction inputs are read-only. The prediction input was already present before evaluation.

```powershell
$workspace = 'D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\work\agent5'
$repo = 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26'
$python = Join-Path $repo '.venv\Scripts\python.exe'
$dataset = Join-Path $repo 'dataset'
$pred = Join-Path $repo '.run\target_v9\sample_partial_predictions.csv'
$env:PYTHONPATH = Join-Path $workspace 'code'

& $python -B -m unittest discover -s (Join-Path $workspace 'code\tests') -p 'test_contract.py' -v
& $python -B -m unittest discover -s (Join-Path $workspace 'code\tests') -p 'test_agent5_*.py' -v
& $python -B (Join-Path $workspace 'code\tools\evaluate.py') $pred --dataset $dataset --report (Join-Path $workspace 'code\evaluation\.agent5_raw_evaluation.tmp.md') --partial
& $python -B (Join-Path $workspace 'code\tools\validate_output.py') $pred --dataset $dataset --requests (Join-Path $workspace 'code\evaluation\agent5_partial_requests.csv')
& $python -B (Join-Path $workspace 'code\tools\agent5_diagnostics.py') $pred --dataset $dataset --report (Join-Path $workspace 'code\evaluation\agent5_sample_diagnostics.md')
```

## Results

- Existing structural contract tests: 6 passed.
- New Agent 5 tests: 6 passed. One initial fixture run failed because its test rows omitted `deletion_status`; the fixture was corrected and the complete final run passed.
- Existing `evaluate.py --partial`: prediction coverage 14/32; status 14/14; exact-step precision 35/67; recall 35/87; positional fields 358/609; exact sequences 0/14.
- `validate_output.py`: PASS, 14 rows satisfy the structural checks and evidence-time bounds for the supplied subset.
- `agent5_diagnostics.py`: PASS; reproduced the same metrics, field/operation breakdowns, top generalized patterns, and retention probe in the saved report.
- Input pre-existed evaluation: last modified 2026-10-25 08:49:58.066 UTC; evaluation started 2026-10-25 09:39:24.997 UTC; SHA-256 before and after was `1a026b60feb81e725078e388dda8a58de29672ed6726ffaf49ff06d12d0d0a50`.
- Agent 0 completed 518 requests with 294 unresolved but produced no root output.csv, so complete target validation was unavailable. No rows were generated or guessed.

The existing evaluator's temporary raw Markdown output contains a mismatch case list and is not part of the staged deliverables. The Agent 5 report suppresses per-case identifiers.


## Final target run and blocker audit

Agent 0's completed status: 518 processed, 294 unresolved, 224 checkpointed rows (80 COMPLETE, 134 INCOMPLETE, 10 NOT_APPLICABLE), no root output.csv. Usage: 724 attempts, 723 successful, 1 failed, 1 retry, 445 hits, 278 misses, 2,619,468 total tokens (1,799,020 input; 820,448 output). No target accuracy was calculated.

The final unresolved list's first-stop families sum to 294: 135 SECURITY_AUDIT_LOG conditions, 68 subject-link classifications, 27 SUPPORT_MESSAGE conditions, 25 BACKUP_ARCHIVE conditions, 2 ACCOUNT_TOMBSTONE conditions, 15 missing scoped-state proofs, 10 workflow-only claims, 4 unclassified material categories, 4 missing subject links, and 4 PRESENT-only flow/export state blockers. See blocker-audit.md for the family-level fixable-versus-evidence-limited triage and limitations.
