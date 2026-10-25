# Ghost Data Still Exists — starter toolkit

This toolkit is a **supplement to**, not a replacement for, the HackerRank organizer repository. It contains original helper scripts, evaluation scaffolding, and a Codex engineering brief. It does not contain organizer data and does not pretend to solve the 518 cases.

## 1. Clone the official repository (PowerShell)

```powershell
git clone https://github.com/interviewstreet/hackerrank-orchestrate-october26.git
cd hackerrank-orchestrate-october26
```

Copy this kit's `code/tools/` and `code/tests/` into the cloned repository's corresponding `code/` directories; also copy `PROMPT_FOR_CODEX.md`, `ENGINEERING_PLAN.md`, `requirements.txt`, `code/evaluation/*.md` and `.gitignore` as needed. **Do not replace the organizer's `AGENTS.md`, `problem_statement.md`, original `README.md`, or dataset files.**

## 2. Create environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Inspect evidence and samples

```powershell
.\.venv\Scripts\python.exe code/tools/inspect_dataset.py
.\.venv\Scripts\python.exe code/tools/index_evidence.py --out work/evidence_index.jsonl
.\.venv\Scripts\python.exe -m unittest discover -s code/tests -v
```

## 4. Start Codex from the organizer repo root

```powershell
codex
```

Ask it to read the organizer's original `AGENTS.md`, `problem_statement.md`, `README.md`, `agent_trace_instructions.md`, and `PROMPT_FOR_CODEX.md` before changing files. Ensure the transcript is captured accurately. This toolkit does not fabricate a development transcript.

## 5. Validate predictions

Once your agent produces root `output.csv`:

```powershell
.\.venv\Scripts\python.exe code/tools/validate_output.py --output output.csv
```

For the sample requests, have your agent generate `work/sample_prediction.csv` *without copying labels from sample_output.csv*, then run:

```powershell
.\.venv\Scripts\python.exe code/tools/validate_output.py --output work/sample_prediction.csv --expected-file sample_deletion_requests.csv
.\.venv\Scripts\python.exe code/tools/evaluate_samples.py --prediction work/sample_prediction.csv --json-report work/sample_metrics.json
```

Then transfer **real measured results** into `code/evaluation/evaluation_report.md`.

## 6. Final submission

Before final submission, independently confirm the official challenge page. Required files include:

- `code.zip` (runnable code + README + `code/evaluation/evaluation_report.md` + `code/evaluation/usage_report.md`)
- root `output.csv` with 518 rows and exact schema
- genuine AI coding transcript (`log.txt` per organizer README, and additional raw session traces if requested by submission UI)
- 30-minute AI interview after submission

Do not include `dataset/`, `.venv`, credentials, `work/`, or nested archives in `code.zip`. The organizer's `agent_trace_instructions.md` additionally describes an `agent-trace.zip`; verify the actual portal slots and instructions, since the README separately directs submission of `log.txt`.

### Known limitations of these tools

The validator checks structure, evidence-ID existence and timestamps. It **cannot judge semantic correctness** of the inferred actions. The evidence indexer is a useful first pass; it needs semantic interpretation of PDFs/images, case identity resolution, reliable per-system snapshots, and activity-event reconciliation. It does not automatically infer final deletion statuses or generate `output.csv`.

### Easier installation (Windows)

From the extracted kit folder, run:

```powershell
.\install_starter.ps1 -RepoPath .\hackerrank-orchestrate-october26
cd .\hackerrank-orchestrate-october26
```

If your PowerShell script execution policy blocks the local script, use the manual clone-and-copy instructions above instead. Inspect any downloaded script before running it.
