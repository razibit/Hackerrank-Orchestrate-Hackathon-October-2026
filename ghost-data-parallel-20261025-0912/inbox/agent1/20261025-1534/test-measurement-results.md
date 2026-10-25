# Agent 1 test and measurement results

## Targeted evidence measurement

Read-only source review covered the two retention-related manifest entries, evidence_27 and evidence_55; the second PDF was a security journal and serves as a non-regression check. The evidence_27 PDF was text-extracted and page 2 visually reviewed. Its six rows show disputed orders, a reason, record date, amount, Retain until date, and owner. They do not state that an active legal hold exists.

Measurement output is under work/agent1/measurements/agent1-retention-20261025-01/ (before.json, after.json, and test logs). For evidence_27, extraction remains 7 observations total (one page-level description plus six resource rows); the six rows remain separate and retain their IDs, locators, timestamps, fields, and source path. Before: 6/6 resource rows were LEGAL_HOLD_RECORD, PRESENT, readback. After: 6/6 are UNRESOLVED, PRESENT, snapshot; scope_id stays empty and scope_complete stays unset. The separate evidence_55 item remains SECURITY_AUDIT_LOG, PRESENT, snapshot.

## Unit tests

Interpreter: D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\.venv\Scripts\python.exe.

Focused command (with PYTHONPATH set to work/agent1/code):

    python -B -m unittest discover -s code\tests -p "test_agent1_*.py" -v

Result: 2 tests passed.

Full command (with PYTHONPATH set to work/agent1/code and GHOST_DATASET_PATH set to the read-only live dataset directory):

    python -B -m unittest discover -s code\tests -v

Result: 72 tests ran; 71 passed and one failed. The sole failure is the existing retention-register test listed in change-summary.md, whose expected category encodes the behavior this patch corrects. An initial full-suite invocation omitted GHOST_DATASET_PATH and failed in dataset-dependent fixtures; the final run used the correct read-only dataset path.

No Foundry calls or full target run were started. The active .run/target_v9 and live checkout were not modified.
