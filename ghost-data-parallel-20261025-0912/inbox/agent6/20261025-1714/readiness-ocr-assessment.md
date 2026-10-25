# Agent 6 read-only readiness and PDF/OCR assessment

Reviewed: 2026-10-25 17:14 +06
Scope: published Agent 0-6 statuses, current evaluation/usage reports, challenge instructions, PDF/image extraction and model request path. Read-only: no active `.run/target_v15` contents, no sample labels/predictions, no organizer truth, no source edits, tests, inference, or external writes.

## Readiness for perfect case processing

The official repository contract asks for **518 target output rows**, not 538; it also has **32 public sample requests**. I found no official 538-row target requirement. See `AGENTS.md` lines 194-202 and `README.md` lines 48-50, 73-75.

Published progress is inconsistent by six cases: Agent 0's latest coordination checkpoint says 54/518 reached with 22 saved case rows, while the current evaluation and usage reports say 61/518 reached with 26 rows saved (8 `COMPLETE`, 18 `INCOMPLETE`). Treat progress as 54-61 reached, 10.4%-11.8%; 22-26 saved rows are 4.2%-5.0% of the target. Those status labels describe inferred deletion state, not correctness against hidden answers. No hidden-target accuracy has been measured and no full output/validation exists. At the 61-request report snapshot, 35 of those reached cases had no saved row; 457 requests had not yet been reached.

For the 32 public cases, v15 resolved 11 (34.38%); 21 (65.63%) remain unresolved. Among the selected 11 only, status accuracy is 10/11 (90.91%), step precision 30/59 (50.85%), step recall 30/76 (39.47%), positional-field accuracy 312/532 (58.65%), and exact ordered sequence 0/11. Every resolved row has a mismatch. Thus none of the 32 is currently evidenced as a fully exact result: 11 are known to have a mismatch and 21 have no prediction. These selected-subset metrics are not all-sample accuracy.

Using the 61/518, 997-second report snapshot, observed throughput is about 3.67 requests/minute. At that rate, the remaining 457 requests alone take roughly 125 minutes (about 2h05); this excludes the 35 already-reached unresolved cases, validation, packaging, and submission. The 54/518 checkpoint implies a similar 2h02. A 90-minute window would need about 5.1 requests/minute before unresolved cases; a 30-minute window would need about 15.2/minute. Current evidence does not support finishing the target run, much less perfect correctness, within 90 minutes. Keep the active run intact; do not invent answers to clear unresolved cases.

The repo's exact October deadline is not configured. HackerRank's current help page describes a 24-hour event beginning Oct 24 at 12:30 UTC, implying Oct 25 at 12:30 UTC if the window is measured from that start. At the environment clock of 11:14 UTC on Oct 25 that is about 76 minutes away. The page does not show a specific portal deadline, so use the user's challenge email/portal timer if it differs; the user's reported ~30 minutes conflicts with this calculated window. Submit soon either way.

## Score and hackathon rubric

The reported 88.8 is user-provided; no leaderboard breakdown was available to verify it. HackerRank's current Orchestrate help page specifies four signals: Code ZIP 30%, Output file 30%, AI interview 30%, and AI chat transcript 10%. “Code” and “Code ZIP” are the same signal; the fifth item in the user's list is the Output file. The total score is a weighted sum, so 88.8 is not a proxy for case accuracy. A 100 final score requires all four signal scores to be perfect; the current case evidence is nowhere near perfect Output quality. The interview and transcript can still demonstrate understanding, iteration, safety, and honesty, but cannot turn wrong or missing output rows into correct answers.

## PDF/OCR status

There is a real structure-loss gap, but extraction is not literally absent. The participant evidence manifest has 4 PDFs and 11 PNGs among 94 files. Current code extracts native PDF text when present; if a page has fewer than 20 text characters it renders a PNG and calls Tesseract `--psm 6`, returning only a text string (`extractors.py:749-784`). It then recognizes a narrow set of pipe-delimited rows and some labeled resource/subject patterns. Otherwise it stores a page-level text observation. The image path uses the same OCR text and heuristics (`extractors.py:800-890`).

The downstream `Observation` retains evidence ID and a line/page locator but no OCR bounding boxes, table grid, cell coordinates, or token confidence (`types.py:12-32`). `observation_to_public_dict` supplies text/fields, and `FoundryChatModel.chat_json` JSON-serializes the payload into a text message (`types.py:45-65`, `model.py:418-460`); no page image is sent for visual interpretation. So columns, row/subject association, reading order, and spatial context can be lost. Tesseract text can be noisy, but “random text” is too broad: simple pipe rows and labeled identifiers are parsed. The verified limitation is lack of general layout-aware extraction and visual evidence reasoning.

We have no measured OCR accuracy/recall or layout extraction benchmark across those 15 PDF/PNG files, so the amount of case loss caused by OCR cannot be quantified. The only cited-PDF diagnostic in the current evidence report is narrow (one cited PDF, 2 pages/1003 extracted characters, no explicit active-hold markers); it does not establish quality across the corpus. Moreover, v15's 21 sample blockers include policy uncertainty, weak/missing identity links, missing grounded IDs, and workflow-only claims; OCR/layout work alone will not solve all of them. Some finance-register examples are correctly unresolved because supplied policy does not say a future retention date is an active legal hold.

A safe structural fix would preserve PDF text spans and word/block coordinates, use table/layout extraction on scanned pages, keep page/crop locators and confidence, and validate extracted IDs/dates/subject-to-resource joins deterministically. For visual tasks, only send rendered page/crops if the authorized runtime model supports image input; require structured outputs with exact page/crop citations and leave low-confidence facts unresolved. This is design guidance only: no OCR fix has been implemented or evaluated in this read-only turn.

## Practical assessment

Perfect performance on all 518 target rows and all 32 sample rows is not realistically supported within the remaining hackathon window. The limiting evidence is unresolved-case volume, zero exact sample sequences, and a target throughput projection longer than the available window; OCR is one contributor but not the only blocker. Preserve correctness gates, do not relax fail-closed rules, and use the remaining time to submit the best valid artifacts possible and explain the system and its measured limits accurately in the interview.

Sources: local `AGENTS.md` and `README.md`; `code/evaluation/evaluation_report.md` and `usage_report.md`; `code/audit_agent/extractors.py`, `types.py`, and `model.py`; official [HackerRank Orchestrate help page](https://help.hackerrank.com/articles/3728112689-hackerrank-orchestrate).
