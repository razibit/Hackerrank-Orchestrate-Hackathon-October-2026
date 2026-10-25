# Evaluation report — Ghost Data Still Exists

> Replace every `TODO` with **measured, reproducible findings**. Never submit as completed with placeholders.

## Environment and run

- Commit/version: TODO
- Timestamp: TODO
- Command: TODO
- Model and configuration: TODO
- Label data: `dataset/sample_output.csv` (32 public cases)
- Generated predictions: TODO path (must be produced without copying sample labels)

## Official sample metrics

| Metric | Measured result |
|---|---|
| Case-level deletion status accuracy | TODO |
| Exact case (status + entire ordered steps) accuracy | TODO |
| Step precision | TODO |
| Step recall | TODO |
| Step F1 | TODO |
| Field-level accuracy (specify alignment method) | TODO |
| Sequence accuracy | TODO |

### Failure analysis and improvements

| Case | Observed error | Root cause | Fix / test | Before | After |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO |

## At least three additional participant-created evaluation cases

1. **Historical email and similar unrelated address:** TODO exact synthetic fixture, expected action and observed output.
2. **Conflicting timestamp/replica evidence:** TODO exact synthetic fixture, expected action and observed output.
3. **Retained security record + tombstone and restore:** TODO exact synthetic fixture, expected action and observed output.

## Regression commands

```bash
python code/tools/validate_output.py --output work/sample_prediction.csv --expected-file sample_deletion_requests.csv
python code/tools/evaluate_samples.py --prediction work/sample_prediction.csv
python code/tools/validate_output.py --output output.csv
```

## Limitations

- TODO measured limitations, failures, and expected impact.
