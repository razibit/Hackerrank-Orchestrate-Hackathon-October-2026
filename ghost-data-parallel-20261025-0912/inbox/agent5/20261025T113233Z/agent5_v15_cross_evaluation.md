# Agent 5 v15 public-sample cross-evaluation

## Integrity and scope

- Source prediction: `hackerrank-orchestrate-october26/.run/sample_v15/partial_predictions.csv` (11 rows; last modified 2026-10-25 10:49:12.016 UTC). It existed before this evaluation and no matching sample-v15 process was active.
- SHA-256 before and after scoring: `12e708bbc2a1ace59facd52aeb27b557ca074a4c225720512c3ebc17168d5565` (unchanged).
- The official evaluator and independent detail evaluator read public labels only after the prediction file existed. In the paired comparison, both prediction files were contract-validated before the evaluator opened public labels.
- No inference was run. I did not access `.run/target_v15`, alter run/cache files, source, Agent 0 reports, or root `output.csv`.

## v15 measured results

| Measure | Result |
|---|---:|
| Coverage | 11/32 (34.38%); 21 cases have no row |
| Status accuracy on supplied rows | 10/11 (90.91%) |
| Exact full-step precision | 30/59 (50.85%) |
| Exact full-step recall | 30/76 (39.47%) |
| Positional field accuracy | 312/532 (58.65%) |
| Exact ordered sequences | 0/11 |
| Subset contract validation | PASS, 11 rows |

These are selection-biased public-sample metrics, not full-sample or hidden-target accuracy. The official and independent evaluators agree with the existing `.run/sample_v15/evaluation_report.md`.

## Cross-run comparison with v14

The full resolved-row reports show v14 at 8/32 and v15 at 11/32. Their selected-row metrics changed by +3 cases (+9.38 percentage points of coverage), +3.41 pp status accuracy, +9.82 pp exact-step precision, +8.10 pp recall, and +4.87 pp positional fields; exact sequence remained 0. These whole-subset deltas are not paired because the resolved sets differ.

On the **eight shared cases**, paired scoring shows no aggregate quality change: status stayed 7/8, exact-step precision 16/39, recall 16/51, positional fields 192/357, and exact sequences 0/8. Per-case exact-step true positives changed in 0/8 shared cases. v15 added three resolved rows; by subtraction from the validated aggregates, those rows contributed 14 exact steps out of 20 predicted and 25 reference steps, with 3/3 statuses correct but 0/3 exact sequences. Thus the aggregate gains reflect added coverage, not better exact-step results on the shared cases.

## General, evidence-grounded improvement targets

1. **Preserve required verification steps.** In v15, operation counts show 19 missing verification steps: 10 `VERIFY_RECORD_ABSENT`, 5 `VERIFY_RECORD_ANONYMIZED`, and 4 `VERIFY_RECORD_PRESENT`. The other operation counts mostly match, while `REDACT_RECORD` and `REPORT_EXPOSED_PII` each appear once more than reference. A general postcondition checklist should retain every applicable, evidence-supported verification for each scoped resource or flow and reject unsupported extras. This targets the largest measured exact-step recall gap without adding case-specific rules.
2. **Carry system/resource locators as one evidence-backed pair.** `system_id` and `resource_id` each match 32/76 positional step locations in the independent per-field breakdown; the existing diagnostic pattern counter records seven joint locator mismatches. Keep both identifiers tied to the same cited observation through findings, remediations, and verification.
3. **Order only after the complete step set is assembled.** Exact ordered agreement is 0/11 overall and 0/8 on shared v14/v15 cases. Missing verification and locator/operation mismatches are present, so sorting alone cannot repair the content. First preserve the full grounded step set, then apply the official deterministic phase/step ordering and numbering.
4. **Treat one-count extra operations as a lower-priority check.** Require direct scoped evidence for each additional redaction or exposed-PII report; the sample contains only one extra of each, so it is weaker evidence than the repeated verification and locator deficits.

These are general remediation directions inferred from measured sample errors; no source change or expected score gain is claimed.

## Measurement caveat

The existing `.run/sample_v15/agent5_diagnostics.md` reports 532 compared positions for each individual field. Its source, `code/tools/agent5_diagnostics.py:205-221,232-241`, increments field matches once per field position but uses the seven-field aggregate (`positional_total`) as each field's denominator. The overall positional score 312/532 is correct. The independently computed per-field denominator is 76 step positions per field; for example, system and resource locators each match 32/76 (42.11%), not 32/532.

## Evidence paths

- Prediction and existing evaluation: `.run/sample_v15/partial_predictions.csv`, `.run/sample_v15/evaluation_report.md`, `.run/sample_v15/agent5_diagnostics.md`.
- Prior public-sample baseline: `.run/sample_v14/partial_predictions.csv`, `.run/sample_v14/evaluation_report.md`.
- Coordinator’s v14/v15 totals: `status/agent0.md:26-27`.
- Independent v15 score and mismatch details: `agent5_v15_detailed_evaluation.md` and `official_sample_evaluation.md` in this inbox.
- Same-case v14/v15 measurement: `paired_v14_v15_cross_evaluation.md` in this inbox.
