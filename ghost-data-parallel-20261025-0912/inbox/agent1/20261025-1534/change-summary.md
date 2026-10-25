# Agent 1 extraction patch

Status: ready for Agent 0 to review and selectively apply.

## Changes

- Retention-register descriptions and rows now yield category UNRESOLVED; only explicit legal-hold evidence yields LEGAL_HOLD_RECORD.
- Structured retention rows keep their observed PRESENT state, but no longer synthesize a record_state=PRESENT field. They therefore retain snapshot proof semantics instead of claiming a readback.
- Every extracted observation now carries the relative manifest source_path in its fields. Evidence ID, row/page locator, observed and available times, system/resource/scope, raw text, and source fields remain intact.
- Added code/tests/test_agent1_extraction.py for the policy distinction and provenance.

## Integration follow-up

The participant policy has no category for a disputed-order retention-register entry. Keep such evidence unresolved until a supported policy treatment is established; do not map it to an active legal hold from PRESENT or a future retention_until date alone. The evidence-classification schema already allows UNRESOLVED, but Agent 0 should ensure downstream classification does not promote this observation back to LEGAL_HOLD_RECORD without explicit hold evidence.

The existing code/tests/test_extractors.py::JsonExtractionTests.test_pipe_delimited_retention_register_is_split_by_subject still expects the old LEGAL_HOLD_RECORD result. Agent 1 did not edit that file due to ownership boundaries; update its expectation during integration to UNRESOLVED / PRESENT / snapshot while retaining its subject-splitting assertions.

No policy, model, prompt, engine, live checkout, active run, or external service was changed.
