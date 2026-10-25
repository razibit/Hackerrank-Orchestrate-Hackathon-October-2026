# Ghost Data Still Exists — ready-to-start kit

Your task: build an investigator that checks whether personal data was really deleted. It reads the supplied fictional records, reports COMPLETE / INCOMPLETE / NOT_APPLICABLE, and gives precisely ordered evidence-backed steps. This is an offline audit and proposed plan; it does not execute deletion against real services.

## What is ready

- Official repository and full dataset at commit acb3dfca6e94e4803a26e72c49074a488de93c93.
- Requirements matrix, policy map, proposed architecture/build order, starter prompt, independent evaluation scenarios.
- Runnable read-only preflight, output contract validator, public-sample metric comparison, and six validator unit tests.
- Honest evaluation/usage report templates and an append-only session log.

The audit agent, model provider integration, evidence extraction pipeline and final predictions are NOT implemented. code/main.py remains the official empty placeholder. Running that file alone does not solve the task. No API inference calls have been made and no output.csv is fabricated.

## Begin on Windows PowerShell

Extract this kit, open its folder in VS Code, and run:

```powershell
py --version
py code/tools/preflight.py
py -m unittest discover -s code/tests -v
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install openai pydantic pypdf pillow pytest
```

Python 3.11+ recommended. Only Python standard library is required for the preparation tools. The listed packages are optional building blocks for the agent, not a locked final dependency set. OCR can use local Tesseract (separate executable installation) or your chosen vision API. Do not paste API keys into the coding conversation. Configure your chosen provider in an uncommitted .env or environment variable; implement .env loading if you choose that route.

Start Codex from this folder, ask it to read AGENTS.md, then paste preparation/FIRST_PROMPT.md. Use a local coding session if you want easier access to original rollout traces. Launching a coding assistant does not automatically provide an API credential to the audit program.

Linux/macOS use python3 in place of py, python3 -m venv .venv, and .venv/bin/python for installations.

## Architecture recommendation

1. Ingestion: parse CSV, text, logs, JSON, isolated SQLite snapshots, PDF text and screenshots. Cache extracted observations keyed by file content hash, extractor version, model and prompt revision. Preserve file_id, capture time, internal event time, source location and raw proof.
2. Identity resolver: use stable user_id and timestamp-aware historical name/email/phone/hash links. Avoid joining unrelated people on weak substrings. Recover as-of identity where the current snapshot is newer than audit_at; do not treat future identity changes as historical facts.
3. Tool-using audit controller: determine request intent; search identifiers; inspect relevant records, replicas and processes; follow grounded resource links; stop under bounded call/step limits. Model text is untrusted until schema and provenance checks pass.
4. Observation store and state reducer: distinguish workflow claims from direct readback; filter by cutoff; scope absence to the actual queried resource and snapshot coverage; resolve conflicting states by time and evidence strength without blindly choosing a newer unrelated file.
5. Policy engine and planner: classify each resource using rule conditions, retain required records, inspect all prohibited tombstone identifiers, detect active recreation paths. Generate actions and final-state checks.
6. Deterministic serializer: choose only allowed status/operation/state values, attach valid citations, apply exact canonical order, number steps, validate, then write CSV atomically.

Use a model for multilingual intent, ambiguous artifacts and multimodal interpretation. Prefer deterministic parsing for structured files, joins, temporal filtering, policy execution and output sorting. Do not send the entire corpus on every case; index once, retrieve proof, and account for extraction/API costs. Start with one controller rather than multiple cooperating agents.

## Build order and suggested remaining-time budget

This is a recommendation, not an event rule. Start times are relative to when you begin.

| Elapsed | Deliverable |
|---|---|
| 0–1 hour | Review policy and several samples; API smoke test; choose model and budget; decide architecture |
| 1–4 hours | Intent, historical identity, text/JSON/log/SQL ingestion, proof store, cutoff enforcement |
| 4–7 hours | PDF + screenshot extraction; state reconstruction; policy/planner; first real sample run |
| 7–11 hours | Evaluate all 32 samples; inspect wrong evidence, missing resources and bad ordering; regression fixtures |
| 11–15 hours | Full 518-case run with checkpoints, retry bounds, extraction cache and usage ledger |
| 15–18 hours | Fix demonstrated failures; rerun affected cases; validate full output and reports |
| 18–20 hours | Clean reproduction, packaging, transcript/trace review; submit with buffer |
| Remaining | Interview preparation, breaks and contingency; honor the live deadline |

Do not defer the first full run until the final hours. Start it as soon as evidence coverage is complete enough to expose runtime and cost problems.

## Evaluation commands after the agent exists

Design the agent CLI to support --requests and --output. Example intended invocation (NOT IMPLEMENTED YET):

```powershell
py code/main.py --requests dataset/sample_deletion_requests.csv --output sample_predictions.csv
py code/tools/validate_output.py sample_predictions.csv --requests sample_deletion_requests.csv
py code/tools/evaluate.py sample_predictions.csv --report code/evaluation/evaluation_report.md
py code/main.py --requests dataset/deletion_requests.csv --output output.csv
py code/tools/validate_output.py output.csv
```

Evaluator accuracy must come from generated predictions, not copied samples. The report tool computes status accuracy, exact-step precision/recall, positional field accuracy, and exact sequence accuracy. It leaves participant-case and improvement sections to complete. A schema PASS does not prove evidence relevance or decision correctness.

The public sample labels contain 10 COMPLETE and 22 INCOMPLETE cases, and NO NOT_APPLICABLE cases. Add explicit non-deletion and negation cases; a high sample score alone cannot validate that branch.

## Final artifacts

Create code.zip only after implementing the agent, filling both reports, and reproducing output.csv. Include README.md with your actual setup/run instructions, code/ with prompts and evaluation reports, and final dependency files. Exclude dataset/, .venv/, caches, credentials, nested archives and this starter ZIP. The official README's package command includes README.md and code/; update it if your final runtime requires root-level dependency files.

Upload code.zip, root output.csv and root log.txt to their specified fields. Preserve agent-trace.zip separately per agent_trace_instructions.md; the extra upload mechanism is unclear, so verify with organizers rather than nesting it in code.zip. See preparation/REQUIREMENTS.md for source discrepancies.

The downloaded starter kit intentionally includes dataset/ so you can begin immediately. It is NOT a submission-ready code.zip.

The live page requires a 30-minute AI interview with camera on. Practice explaining: intent gating; historical identifiers; why a successful workflow is not proof; a replica-drift example; retained records/tombstones; cutoff filtering; exact ordering; your measured failures, token costs and limitations. Use Decision → Reason → Implementation → Evidence → Limitation.

Sources: [challenge](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists), [repository](https://github.com/interviewstreet/hackerrank-orchestrate-october26), problem_statement.md, README.md, AGENTS.md, agent_trace_instructions.md, and participant-facing dataset/.
