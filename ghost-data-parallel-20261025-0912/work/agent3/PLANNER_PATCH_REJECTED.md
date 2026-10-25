# Planner verification evidence-ID patch: rejected

Status: **Rejected on output-contract grounds. Do not integrate.**

The isolated candidate removed `plan_case`'s blanket clearing of verification `evidence_id` values for `INCOMPLETE` results. Agent 0 reported that replaying the 11 cached sample predictions increased exact steps from 30/59 to 32/59, recall from 30/76 to 32/76, and matching fields from 312/532 to 315/532. However, the official partial evaluator and detailed validator rejected three non-empty evidence IDs on `INCOMPLETE` verification steps in `case_27`. The contract requires empty evidence IDs for proposed remediation and future verification checks in `INCOMPLETE` results, so the measured score gain does not justify the invalid output.

No replacement variant is proposed. The experiment did not establish a contract-valid way to improve those matches. The isolated source change remains only as a rejected review artifact; the live v15 package, process, reports, and run artifacts were not modified by Agent 3.
