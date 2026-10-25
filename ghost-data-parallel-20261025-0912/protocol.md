# Parallel work coordination

Baseline: `baseline/` is the immutable current-source snapshot captured from the live checkout (uncommitted code included; `.git`, datasets, `.run`, `.venv`, credentials, archives, and root logs excluded).

Agent 0 owns the real checkout and active target run. Agents 1-5 edit only `work/agentN/`; Agent 6 reads `baseline/`, workspaces, and inboxes but never edits source. All input datasets live read-only at `D:\Hackerrank Orchastrate Hackathon 2026\hackerrank-orchestrate-october26\dataset`.

Status is one file per owner: `status/agent0.md` through `status/agent6.md`. Alerts and review decisions are written only by Agent 6 in `alerts/` and `decisions/`. Deliverables go to `inbox/agentN/<timestamp>/` with changed files under their repository-relative paths, a `change-summary.md`, exact test commands/results, and a `log-fragment.txt` for Agent 0 to serially append to the official repository log. Never edit the live checkout or another agent's files.

Foundry lease: Agent 0 owns the currently active target run. No other agent may call Foundry until Agent 0 posts a release of the GPU lease; thereafter Agent 6 schedules one inference process at a time. Reuse read-only prediction/checkpoint artifacts where useful. This controls concurrency, not total authorized calls.

Integration: Agent 0 reviews and manually applies selected inbox files, runs relevant regression tests and sample evaluation, and keeps the last passing implementation if a change regresses. No commits, branch switches, pushes, uploads, or real deletions.
