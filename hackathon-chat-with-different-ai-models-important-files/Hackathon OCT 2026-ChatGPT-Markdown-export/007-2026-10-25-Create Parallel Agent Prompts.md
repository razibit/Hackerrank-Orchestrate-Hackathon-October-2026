---
title: "Create Parallel Agent Prompts"
project: "Hackathon OCT 2026"
project_id: "g-p-6adc978cca0c8191bfc5c869781abbe3"
conversation_id: "6addc683-034c-83ec-ad68-227490c4ea5e"
created_at: "2026-10-25T09:06:11.458Z"
updated_at: "2026-10-25T09:11:19.984Z"
source: "https://chatgpt.com/g/g-p-6adc978cca0c8191bfc5c869781abbe3/c/6addc683-034c-83ec-ad68-227490c4ea5e"
---

# Create Parallel Agent Prompts

## User

I want to create 6 total agent sessions. In that agent session, the current session that is currently running and doing things single-handedly, I want to divide all the tasks into 5 different agent sessions. Those sessions will be running simultaneously to complete it within the remaining 3 hours for the hackathon.

All those agents have to work toward one single goal: to make our agent perform better, be more accurate, and get a higher total score. Currently, the total score is 88.8. We want to beat it by 95+ so that we can secure first position.

I want to ask the current session that is running to give me 5 total prompts. Those 5 prompts will divide the work into 5 different agent sessions and the current running agent session. In total, 6 agents will work to make the agent more accurate, more reliable, and top-performing. If we add the current running agent, then in total we get 7 agents. The 6 agents will be splitting their work into 6 different agent sessions, so we don't need to split it in the current agent session. The current agent session will divide its own work. The new 5 agent sessions and the agent session can run independently without overwriting each other's work. They are split in a way that they work convergently, but they don't overwrite each other's work. They work simultaneously.

Currently, we have rented a GPU. The GPU doesn't have any API rate limits because we rented the entire GPU, so there is no rate limit constraint. We can make millions of API calls into that, so we will utilize that.

Another thing is that one agent out of those 7 total agents will check all the work. It will orchestrate all the agents. It will check what each agent is doing. If one of the agents is going wrong, it can instantly let the agent that was going in the wrong direction, doing wrong, or did something wrong know it. We have to do all these things within 3 hours because we have very little time, so that we can start working on the agents in parallel 

i have given you the current running agents work details.

We'll paste your now-created prompt to the currently running agent to generate six total new agent sessions. It will give me six different prompts from its current working knowledge, letting the current running agent know that it is splitting its own work. It will assign all these things to itself from its knowledge, as it is currently working singly on everything. I will create six new agent sessions that will work in parallel.

## Assistant

The setup should be **7 parallel agents total**: your existing Codex session remains the main implementation and integration agent, while you launch **5 specialist agents and 1 orchestration/supervision agent**.

The following prompt tells your current Codex agent to generate six separate, ready-to-paste prompts using its actual knowledge of the repository, existing code, unresolved cases, evaluations, and active GPU inference run.

<WritingBlock id="67142" variant="document"># URGENT: Split Current Hackathon Work Across 7 Parallel AI Agents

We have approximately **3 hours remaining** in the HackerRank Orchestrate October 2026 hackathon.

You are currently the primary Codex agent implementing **Ghost Data Still Exists**, and you have been handling the entire project single-handedly.

**Your immediate task is to generate exactly SIX complete, independent, ready-to-paste prompts for SIX NEW Codex agent sessions.**

You will remain active as the seventh agent.

I will manually launch all six new sessions using your generated prompts. You must use your existing working knowledge of the repository, current implementation, completed experiments, outstanding defects, model configuration, evaluation results, and active processes to distribute work intelligently.

## 1. Our single shared objective

Our objective is to maximize the final hackathon score, targeting **95+ out of 100**, and outperform the current leading score of approximately **88.8**.

This is an ambitious target, not a guaranteed outcome.

Every agent must contribute directly to:

- Increasing prediction accuracy.
- Improving completeness and validity of `output.csv`.
- Improving reasoning accuracy and the ordering of remediation steps.
- Resolving the maximum number of currently unresolved cases.
- Improving evidence extraction, identity resolution, policy interpretation, and temporal reasoning.
- Strengthening robustness, reproducibility, and submission quality.
- Maximizing the overall weighted hackathon score rather than optimizing a single metric in isolation.

**Prioritize improvements by their expected effect on actual scoring and their feasibility within the remaining time.**

Do not waste time on speculative architectural rewrites, unnecessary features, or cosmetic improvements.

## 2. Exactly seven agent sessions

The final structure must be:

- **Agent 0 — You, the existing running Codex session:** Primary implementation owner, integration authority, final evaluation, final output generation, and submission packaging.
- **Agent 1 — New specialist session:** Independently assigned high-impact engineering responsibility.
- **Agent 2 — New specialist session:** Independently assigned high-impact engineering responsibility.
- **Agent 3 — New specialist session:** Independently assigned high-impact engineering responsibility.
- **Agent 4 — New specialist session:** Independently assigned high-impact engineering responsibility.
- **Agent 5 — New specialist session:** Independently assigned high-impact engineering responsibility.
- **Agent 6 — New orchestration session:** Dedicated supervisor, cross-agent reviewer, defect detector, progress tracker, and coordination authority.

The six new sessions must be capable of working concurrently with your existing session.

You must decide the most effective distribution based on your actual understanding of the codebase.

A suggested specialization is:

1. Evidence extraction, normalization, and provenance.
2. Identity matching, historical aliases, and temporal state reconstruction.
3. Policy interpretation, retention conditions, remediation planning, and step ordering.
4. LLM prompting, structured inference, and reasoning quality.
5. Independent evaluation, adversarial testing, diagnostics, and output correctness.
6. Independent orchestration, cross-agent QA, supervision, and coordination.

**These are suggestions, not mandatory assignments.** You have better firsthand knowledge of the current system. Modify the allocation if another division will produce a greater score improvement.

Avoid allocating agents to problems already solved unless additional work there has a concrete expected benefit.

## 3. First assess the CURRENT state

Before creating the six prompts, quickly inspect the current repository and available checkpoints.

You already have extensive working knowledge, so do not repeat the entire research or preparation process.

Determine:

- Which code modules and workflows already function correctly.
- Which bugs, limitations, or missing capabilities have the greatest impact on accuracy.
- The latest completed and ongoing evaluation results.
- The current 518-case execution state.
- The causes of unresolved cases.
- The reasons for incorrect or missing remediation steps.
- Which experiments are still running.
- Which files and processes your current session actively owns.
- Which components can be safely delegated.
- Which work should remain exclusively under your control.

Previous checkpoints indicated serious gaps in case resolution and exact remediation-step agreement, but those numbers may now be outdated.

**Use the latest actual state, not outdated checkpoint assumptions.**

Do not interrupt, cancel, overwrite, or restart the active target run just to create this delegation plan.

## 4. Absolutely prevent agent conflicts

This is a critical requirement.

All seven agents must work toward the same goal while having independently owned responsibilities.

They must not overwrite each other's work or corrupt active processing.

Design a safe parallel execution strategy that addresses:

- Exclusive file and module ownership.
- Shared-file read permissions.
- Isolated temporary directories.
- Independent test and evaluation outputs.
- Separate inference cache or checkpoint namespaces where necessary.
- Safe code integration.
- Concurrent GPU usage.
- Shared progress and coordination records.
- Conflict detection and resolution.

Inspect the actual Git working-tree state first.

The current checkout may contain uncommitted changes, untracked files, active run artifacts, and cached inference results. Do not assume that creating Git worktrees from HEAD automatically preserves the current implementation.

Choose an isolation strategy that preserves the real working baseline.

You may use isolated working copies, safe worktrees, or strict ownership-controlled directories, whichever is most appropriate for this environment.

**Do not allow multiple agents to modify the same shared file concurrently.**

When an agent needs changes in another agent's module, it must produce a patch, isolated candidate implementation, or precise change proposal for the file owner or primary integration agent.

You remain the final authority for integration and release.

Do not commit, push, switch the current working branch, upload a submission, or perform destructive operations unless explicitly authorized.

All sessions must follow `AGENTS.md` and the official challenge requirements.

## 5. Dedicated orchestrator: Agent 6

One of the six new agents must work exclusively as the **Orchestrator / Supervisor / Quality Controller**.

Its mission is not to implement features independently.

Its mission is to help all seven agents work correctly, efficiently, and cohesively.

It must:

1. Maintain visibility into the assignments, status, progress, blockers, and deliverables of all seven agents.
2. Review their test results, implementation changes, proposed patches, and evaluation evidence.
3. Detect incorrect assumptions, regression risks, overlapping modifications, stalled work, or optimization in the wrong direction.
4. Alert the responsible agent whenever a problem is identified.
5. Escalate cross-agent conflicts and integration risks to Agent 0.
6. Compare improvements against measurable baseline results.
7. Identify duplicated effort or neglected high-impact problems.
8. Recommend urgent task reprioritization based on remaining time.
9. Maintain a continuously updated integration and release-readiness checklist.
10. Ensure that proposed improvements support general correctness rather than case-specific answer fitting.

Establish a real communication mechanism.

If direct agent-to-agent messaging is supported, use it. Otherwise, establish shared coordination files containing status, alerts, recommendations, and integration requests.

Every agent must explicitly check incoming coordination alerts at frequent milestones, ideally at intervals of 1–2 minutes when practical.

The orchestrator should review updates frequently, but do not claim instantaneous delivery if the environment only supports periodic polling.

The orchestrator must have an explicit escalation protocol for critical problems.

**Agent 6 must never overwrite another agent's implementation or interfere with the active inference run.**

It can recommend changes, request corrections, and block unsafe integration through the agreed coordination process. Agent 0 retains final integration authority.

## 6. GPU inference and experimentation

We currently rent the GPU running the Azure Foundry inference deployment.

The GPU is charged on a time basis, rather than through ordinary per-request API billing.

Therefore:

- Do not impose an arbitrary $30 API-token spending cap on experimentation merely because earlier runs used that assumption.
- There is no user-imposed API call count limit for this parallel optimization effort.
- Agents may conduct independent LLM experiments where they can produce measurable improvements.
- Reuse existing inference results whenever possible.
- Prioritize experiments with high expected accuracy gains.

However, unlimited permitted requests do not mean unlimited hardware throughput.

The agents must respect actual GPU concurrency, throughput, memory, queueing behavior, context limits, and deployment availability.

Avoid launching seven uncontrolled inference workloads simultaneously.

The existing full target run must be protected from starvation or resource contention.

Design a practical shared-GPU coordination strategy, giving priority to critical evaluations and final prediction generation.

We want maximum useful experimentation and maximum score improvement within three hours, not maximum API call volume.

Never expose credentials, create unauthorized deployments, or modify the rented infrastructure without explicit authorization.

## 7. Preserve evaluation integrity

All agents must comply with the official challenge contract.

In particular:

- Do not use target labels or expected answers as runtime prediction inputs.
- Keep sample prediction generation separate from sample-answer evaluation.
- Do not hardcode solutions for specific case IDs.
- Do not invent evidence, citations, timestamps, or policy requirements.
- Do not manufacture successful accuracy metrics.
- Evaluate changes against independent tests and available authorized evaluation evidence.
- Preserve correct fail-closed behavior where required by the contract.
- Distinguish genuinely missing evidence from failures of extraction, retrieval, or reasoning.

One major deliverable is a **complete, schema-valid 518-row `output.csv`**, produced according to the official rules.

Investigate ways to resolve or represent uncertain cases that the contract permits, without inventing facts or silently weakening correctness.

Improve exact remediation-step content and ordering, not merely case-status classification.

## 8. Three-hour execution strategy

Create a time-sensitive coordination plan.

Suggested allocation:

| Phase | Time budget |
|---|---|
| Session setup, ownership, and baselines | First 10–15 minutes |
| Independent high-impact engineering and experiments | Next 75–90 minutes |
| Integrate and compare improvements | Next 25–35 minutes |
| Final complete evaluation and validation | Next 20–30 minutes |
| Packaging, sanity checks, and release handoff | Remaining time |

Adapt this plan based on the actual submission cutoff, remaining time, and inference runtime.

Do not wait until the end to begin integration. Deliver improvements incrementally when safe.

If a specialist's work is not ready near the integration deadline, preserve the last known working implementation rather than risking a late regression.

**Our priority is a valid and accurate submission before the deadline, not a theoretically perfect system delivered too late.**

## 9. Requirements for each generated agent prompt

Produce SIX complete prompts.

Each prompt must be fully self-contained so I can paste it into a completely new Codex session.

Every prompt must include:

**A. Identity and objective**
- Unique agent number and role.
- Shared hackathon objective.
- Precise assigned problem.
- Why the problem matters to the final score.

**B. Repository and operating context**
- Exact Windows repository location.
- Relevant existing files and modules.
- Required instructions and challenge contracts.
- Existing implementation that must be preserved.
- Assumptions that must be verified at startup.

**C. Exclusive responsibilities**
- Specific modules, components, and tasks the agent owns.
- What it must investigate.
- What it must implement or evaluate.
- What it explicitly must not modify.
- Dependencies on other agents.

**D. Execution instructions**
- Immediate first actions.
- Prioritized engineering tasks.
- How to run relevant tests.
- How to evaluate improvements.
- How to use inference resources safely.
- How to preserve existing checkpoints.

**E. Communication protocol**
- Where to publish status.
- Where to receive orchestrator alerts.
- How to report important findings.
- How to request changes in another agent's module.
- How to submit changes for integration.
- How to report an urgent blocker.

**F. Acceptance criteria**
- Concrete technical deliverables.
- Tests that must pass.
- Metrics or behavioral outcomes to measure.
- Evidence needed to substantiate improvements.
- A clear completion condition.

**G. Restrictions**
- No conflicting modifications.
- No unsupported output fabrication.
- No unauthorized destructive operations.
- No unnecessary full reruns.
- No exposure of secrets.
- No unapproved submission.
- Follow `AGENTS.md`, including the required logging and trace procedures.

For Agent 6, replace feature-implementation tasks with an explicit monitoring, review, communication, escalation, and coordination workflow.

Each prompt must be operational, not a vague job description.

Do not use placeholders such as "insert relevant module here." Inspect the repository and provide real paths and actionable responsibilities.

## 10. Shared coordination infrastructure

Define the exact coordination mechanism all seven agents will use.

Prefer a simple filesystem-based system if no reliable direct inter-agent messaging exists.

It must support:

- Agent identities and assignments.
- Exclusive ownership mapping.
- Regular progress reports.
- High-priority alerts.
- Integration requests.
- Test and metric summaries.
- Pending integration decisions.
- Final release readiness.

Separate these internal working artifacts from submission materials unless official rules explicitly require them.

Ensure status writing is isolated so agents do not overwrite each other's reports.

The generated prompts must all refer to the same coordination conventions.

The orchestrator must be able to determine which agent owns any disputed file or responsibility.

## 11. Your own role after delegation

You are **Agent 0**.

You must not stop implementing simply because work has been distributed.

Continue owning:

- The active target evaluation and its checkpoints.
- Shared-system integration.
- Cross-component regression testing.
- Final end-to-end execution.
- Final `output.csv` generation and validation.
- Final source packaging.
- Submission artifact verification.
- Release-readiness decisions and handoff to me.

Avoid modifying modules exclusively assigned to specialists until their changes are ready for integration, unless an urgent blocking issue requires reassignment through the agreed coordination process.

The orchestrator will review your progress as well.

All agents, including you, are subject to the same quality and coordination standards.

## 12. Required response — generate the prompts NOW

Your next response must contain, in this exact order:

### Part 1 — Current state and task allocation

A concise snapshot of the current project state and the highest-impact remaining issues.

Then a table showing all seven agents, their assignments, exclusive file ownership, expected deliverables, and dependencies.

### Part 2 — Parallel execution protocol

The exact isolation, communication, monitoring, GPU-sharing, and safe integration strategy.

Provide any essential setup commands.

### Part 3 — Six individual copy-paste prompts

Output six clearly separated complete prompts:

**PROMPT 1 — AGENT 1**

**PROMPT 2 — AGENT 2**

**PROMPT 3 — AGENT 3**

**PROMPT 4 — AGENT 4**

**PROMPT 5 — AGENT 5**

**PROMPT 6 — AGENT 6: ORCHESTRATOR**

Each must work as a standalone initial Codex session instruction.

### Part 4 — Launch instructions

Tell me the recommended launch order, whether any one-time isolation setup is needed, and which prompts can be launched immediately in parallel.

Make sure I can launch all six new sessions without further planning.

### Part 5 — Your continuing work

State what you, Agent 0, will continue doing while the other six agents work, including how you will safely integrate their results.

---

# FINAL PRIORITY

**We have approximately three hours. Generate all six agent prompts immediately, using your actual current project knowledge.**

Do not spend substantial time recreating existing research.

Do not pause or damage the active evaluation process.

Do not produce generic prompts disconnected from the repository.

Do not create a system where all seven agents edit the same files.

The six new agents must be independently productive, mutually compatible, and coordinated by one dedicated supervisor.

**One shared goal: maximize legitimate measured accuracy, complete the submission, and achieve the highest possible hackathon score before the deadline.**

Produce the six prompts now so I can immediately launch all six Codex sessions.</WritingBlock>

**Important:** The dedicated supervisor will only be able to correct other sessions quickly if they share a working communication mechanism. The prompt explicitly requires that instead of assuming separate Codex sessions can automatically talk to one another.

It also keeps the existing running agent responsible for the final integration and submission artifacts, preventing seven independent implementations from diverging.
