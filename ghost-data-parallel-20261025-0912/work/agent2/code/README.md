# Ghost Data Still Exists audit agent

This folder is the submission source. It reads the participant-provided dataset, extracts evidence into a versioned local cache, asks the configured Microsoft Foundry deployment to classify request intent and candidate evidence, reconstructs audit state deterministically, and emits `output.csv` only when every request is resolved and the official structural validator accepts the complete output.

The agent never performs deletion. Its steps are findings, proposed remediation, and verification instructions. It fails closed on ambiguous identity, missing temporal support, unresolved conditional policy, unsafe restore or sync state, malformed model output, or incomplete request coverage.

## Requirements

- Python 3.12 (the runtime used for the recorded tests and inference)
- An Azure CLI login authorized for the configured Microsoft Foundry endpoint, or an existing local `AZURE_FOUNDRY_API_KEY`
- The challenge dataset in a separate `dataset/` directory

Install the packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code\requirements.txt
```

Set the endpoint and deployment in the process environment. Do not put credentials in source files, logs, or archives. The agent accepts the non-secret values from environment variables or an ignored local `.env.local` file. To use Azure CLI authentication, sign in first with `az login` and select the intended subscription. A local API key is optional and must remain outside submitted artifacts.

```powershell
$env:AZURE_FOUNDRY_ENDPOINT = "https://<your-foundry-endpoint>"
$env:AZURE_FOUNDRY_DEPLOYMENT = "<deployment-name>"
$env:AZURE_FOUNDRY_MODEL_NAME = "<model-name>"
```

Run preflight, unit tests, and then inference:

```powershell
.\.venv\Scripts\python.exe -B code\tools\preflight.py --dataset .\dataset
$env:GHOST_DATASET_PATH = (Resolve-Path .\dataset).Path
.\.venv\Scripts\python.exe -B -m unittest discover -s code\tests -v
.\.venv\Scripts\python.exe -B code\main.py `
  --dataset .\dataset `
  --output .\output.csv `
  --cache-dir .\.cache\audit_agent `
  --run-dir .\.run\audit_agent `
  --max-model-calls 0 `
  --allow-uncapped-gpu-hours
```

`--max-model-calls 0` disables the request-count cap; use a positive value when a hard call bound is desired. Individual provider failures still receive at most three attempts. The owner authorized uncapped Foundry GPU-hour billing for this run, so it uses `--allow-uncapped-gpu-hours`. To enforce a USD budget instead, configure a verified hourly accelerator rate, accelerator count, billing start, and `MAX_RUN_COST_USD`; the program refuses to infer a rate. A USD estimate remains unavailable when the provider does not return a rate or billable-hour record.

The program requires Microsoft Foundry and never replaces model inference with a deterministic-only prediction path. Evidence extraction, identity/time checks, policy application, remediation ordering, and output validation are deterministic. Model responses are schema-checked, cited to supplied evidence identifiers, and cached by source/prompt/model/data fingerprint. The CLI has no request-count cap by default; specify a positive `--max-model-calls` value to set one.

For a no-inference replay from an existing complete response cache, pass `--cache-only`. The agent then fails closed on any cache miss and does not contact the provider. This is useful for reproducibility checks and package validation; it does not provide a fallback solver.

Build the submission archive from the explicit inclusion list and verify its contents and CRC:

```powershell
python -B code\tools\package_submission.py --output .\code.zip
```

## Evaluation and reproducibility

The actual prompts are in `prompts/`. Evaluation-only code is in `evaluation/` and `tools/evaluate.py`; the evaluator reads `sample_output.csv`, while `main.py` does not. Run the evaluator only after producing a complete 32-row sample prediction file:

```powershell
.\.venv\Scripts\python.exe -B code\tools\evaluate.py .\sample_predictions.csv `
  --dataset .\dataset `
  --report code\evaluation\evaluation_report.md
```

The target dataset contains 518 requests. The agent writes no final CSV if any case is unresolved. Run-specific checkpoints, response caches, and detailed provider usage belong under ignored `.run/` and `.cache/` paths, not in the code archive. See `evaluation/evaluation_report.md` and `evaluation/usage_report.md` for measured results and limitations.
