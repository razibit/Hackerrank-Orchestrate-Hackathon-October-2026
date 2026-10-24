# Ordered implementation roadmap

Preparation is not implementation. Existing tools validate structure and compare predictions; they do not infer answers. Replan effort from the authenticated cutoff, not historical countdowns.

| Priority / phase | Work | Output | Acceptance |
|---|---|---|---|
| P0 / 0 | Complete semantic reading from review-progress.json | Closed ledger and revised decisions | **Complete:** 74 unique files, 213 chunks, 18,704 lines; all source hashes and normalized checkout copies verified; no unreadable evidence |
| P0 / 1 | Verify portal cutoff/interview/trace slots; select model/access/budget | Sourced rules and configuration decision | Timestamped evidence; hidden credential entry; tested provider access |
| P0 / 2 | CLI, types, time-aware identity and raw observations | General synthetic vertical slice | Correct authorization; missing identity unresolved; no label access; cutoff enforced |
| P0 / 3 | Schema-specific adapters and indexes for all formats | 94-file provenance-preserving coverage | No silent omissions; complete log context; replica scopes; visual spot checks |
| P0 / 4 | Investigator, state reducer, conditional policy, planner and serializer | First genuine sample_predictions.csv | Every component participates; no forced success or copied labels |
| P0 / 5 | Full public/custom evaluation | Markdown metrics and case diffs | Zero schema errors; every mismatch diagnosed; >=3 executed end-to-end custom cases; 32/32 sample target without leakage |
| P1 / 6 | Checkpointed full trial with usage and ambiguity queues | Runtime/cost/coverage facts | 518 unique IDs attempted; failures explicit; finalization blocks unresolved cases |
| P1 / 7 | Targeted fixes and cold/warm reproduction | Final output.csv and reports | 518 grounded valid rows; fixed-observation output identical; fresh extraction variance disclosed |
| P0 / 8 | Clean replay, package allowlist, README, dependency capture and secret/trace review | code.zip, output.csv, log.txt; separate raw trace if supported | Fresh run works; reports match run/output; each upload <=50 MB; no excluded assets/nested archives |
| P0 / 9 | Submit and complete interview | Receipt and completion evidence | User-controlled portal confirmation within verified windows |

## First vertical slice

Proposed CLI: --requests, --output, --limit; separate evaluation mode. Create only useful modules, not unused scaffolding. Start with an isolated synthetic dataset: old email links to residual search record plus enabled connector. Expect grounded findings, DISABLE_DATA_FLOW before DELETE_RECORD, then required verification with future evidence IDs blank. Add a negated data-copy request producing NOT_APPLICABLE solely from request meaning. Missing identity becomes an internal error, not a public answer.

Do not replace main.py with the Gemini reference engine. The review gate is closed; implementation may now begin. No release while unresolved facts, measured reports or portal rules are outstanding. Failed checks cannot be replaced by README claims.
