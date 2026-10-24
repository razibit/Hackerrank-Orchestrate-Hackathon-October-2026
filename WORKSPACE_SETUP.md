# Workspace setup

Research root: `D:\Hackerrank Orchastrate Hackathon 2026`.
Implementation root: `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26`.
The similarly named `D:\HR Orchastrate Hackathon 2026` supplies a strategy document only. Preserve the existing checkout/branch; no second clone is needed. No branch changes, commit, fetch or push were performed.

## Working preparation commands

Python 3.11+ recommended; inspection used installed CPython 3.12. Preparation tools require only the standard library; no pip packages needed.

```powershell
Set-Location -LiteralPath 'D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26'
python --version
python -B code/tools/preflight.py
python -B -m unittest discover -s code/tests -v
```

Both checks passed here. `-B` avoids bytecode caches. Installed S2 validator uses a positional output path; do not mix S3's --output syntax.

```text
research root/
  consolidated Markdown documents
  research/
    inventory.json, source-files.csv, review-progress.json
    structural-checks.json, reference-probes.json
    FILE_ANALYSIS.md, VISUAL_REVIEW.md, VERIFICATION.md
    official/       frozen official Markdown
    reading/        lossless temporary reading batches, not inference data
    visual-review/  rendered PDF pages and contact sheets
  hackerrank-orchestrate-october26/  existing official checkout
    original README, AGENTS, problem statement, trace instructions
    dataset/        unchanged official participant data
    code/main.py    still empty
    code/tools/     contract, preflight, evaluate, validate_output
    code/tests/     six contract tests
    code/evaluation/ empty main.py, unmeasured templates, proposed cases
    log.txt         append-only preparation log
    .env.example    empty planning template
    .gitignore      secrets/cache/output exclusions
```

## Runtime prerequisites still undecided

No inference provider/model, API credential, budget or final dependency lock has been selected/tested. A coding subscription does not establish runtime API access. `.env.example` is a planning template; MODEL_API_KEY is a proposed adapter convention, not an implemented SDK setting. Environment loading/validation must be written explicitly. Enter secrets locally through a hidden flow; never paste them into chat or package `.env`.

Host Python can import Pillow, PyMuPDF (fitz) and OpenAI; Tesseract is discoverable; pypdf is absent. These facts do not establish inference readiness or a reproducible environment. PDF review used fitz. S3's indexer specifically needs pypdf and does not automatically use fitz. Choose and pin one reviewed extraction stack after corpus review.

Optional future environment creation, not executed:

```powershell
python -m venv .venv
# Install a reviewed final requirements.txt only after it exists.
```

requirements-preparation.txt is informational and needs no install. Final code.zip must include the actual dependency file/instructions.

## Intended commands AFTER implementation

These interfaces are proposed; main.py currently implements none of them:

```powershell
python code/main.py --requests dataset/sample_deletion_requests.csv --output sample_predictions.csv
python -B code/tools/validate_output.py sample_predictions.csv --requests sample_deletion_requests.csv
python -B code/tools/evaluate.py sample_predictions.csv --report code/evaluation/evaluation_report.md
python code/main.py --requests dataset/deletion_requests.csv --output output.csv
python -B code/tools/validate_output.py output.csv
```

Empty main.py execution is not a baseline. Evaluator overwrites its report destination; preserve custom-case/improvement prose until composing the final report. S3 installer was inspected but not run because its force-copy can replace existing assets.

## Logs

Follow official AGENTS.md. Append exact prompts with secrets redacted; use authoritative harness/model metadata, not invented identifiers. Current session: tool=Codex, model=gpt-6.1-sol from rollout metadata. Do not rewrite old imported logs to pretend missing metadata was available. Preserve original relevant traces separately; sanitize staged copies and exclude unrelated sessions/authentication files. Portal upload details remain open.
