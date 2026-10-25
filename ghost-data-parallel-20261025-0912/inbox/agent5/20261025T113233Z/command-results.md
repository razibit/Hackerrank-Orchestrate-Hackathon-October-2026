# Agent 5 v15 evaluation command results

- Checked coordination alerts and status before evaluation. The v15 sample prediction artifact was `.run/sample_v15/partial_predictions.csv`; the file existed and no sample-v15 Python prediction process was active.
- Prediction last-write time before evaluation: `2026-10-25T10:49:12.0166179Z`.
- Prediction SHA-256 before and after independent evaluation: `12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565` (unchanged).
- Official evaluator `code/tools/evaluate.py <partial_predictions.csv> --dataset dataset --report <inbox>/official_sample_evaluation.md --partial`: exit 0. Metrics: 11/32 coverage; status 10/11; exact steps 30/59 precision and 30/76 recall; positional fields 312/532; order 0/11.
- Official validator `code/tools/validate_output.py <partial_predictions.csv> --dataset dataset --requests <inbox>/subset_sample_requests.csv`: exit 0; PASS for all 11 supplied rows.
- Independent detailed evaluator `evaluate_v15_checkpoint.py`: exit 0; no contract errors; its metrics match the official evaluator.
- Paired cross-evaluator `cross_evaluate_v14_v15.py`: exit 0 after validating both existing prediction files and before reading public labels. Common set 8/32; v15 and v14 each scored status 7/8, step precision 16/39, recall 16/51, positional fields 192/357, exact sequence 0/8. Exact-step TP changes: 0/8.
- v14 hash before/after paired evaluation: `d80b4d332a049ff8f60364b8fc593c139041939b44b0a1c787f6e731654a6848` (unchanged). v15 hash before/after paired evaluation: `12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565` (unchanged).
- No model/provider calls, inference, source edits, target-v15 reads, root-output edits, or overwrites of Agent 0 reports were made. All new artifacts are confined to this Agent 5 inbox; the only shared coordination edit is `status/agent5.md`.

## Reproduction commands

Run these from PowerShell; they use the existing prediction files and do not invoke the agent:

```powershell
$repo='D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26'
$stage='D:\Hackerrank Orchastrate Hackathon 2026\ghost-data-parallel-20261025-0912\inbox\agent5\20261025T113233Z'
$py=Join-Path $repo '.venv\Scripts\python.exe'
& $py -B (Join-Path $repo 'code\tools\evaluate.py') (Join-Path $repo '.run\sample_v15\partial_predictions.csv') --dataset (Join-Path $repo 'dataset') --report (Join-Path $stage 'official_sample_evaluation.md') --partial
& $py -B (Join-Path $repo 'code\tools\validate_output.py') (Join-Path $repo '.run\sample_v15\partial_predictions.csv') --dataset (Join-Path $repo 'dataset') --requests (Join-Path $stage 'subset_sample_requests.csv')
& $py -B (Join-Path $stage 'evaluate_v15_checkpoint.py') --repo $repo --dataset (Join-Path $repo 'dataset') --predictions (Join-Path $repo '.run\sample_v15\partial_predictions.csv') --report (Join-Path $stage 'agent5_v15_detailed_evaluation.md')
& $py -B (Join-Path $stage 'cross_evaluate_v14_v15.py') --repo $repo --dataset (Join-Path $repo 'dataset') --baseline (Join-Path $repo '.run\sample_v14\partial_predictions.csv') --candidate (Join-Path $repo '.run\sample_v15\partial_predictions.csv') --report (Join-Path $stage 'paired_v14_v15_cross_evaluation.md')
```
