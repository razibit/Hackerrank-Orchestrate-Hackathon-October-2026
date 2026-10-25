# DataLab OCR candidate (v16)

The shared source checkout has a DataLab-backed candidate for future extraction. PDF pages are rendered to temporary 300-DPI PNGs, and PNG inputs are sent directly to DataLab structured extraction. Both request modes are set to `accurate`; the output schema asks for visible transcription and table rows, and preserves provider citations and field metadata. No Tesseract fallback remains in the runtime path.

The dependency is pinned as `datalab-python-sdk==0.5.0`. The extraction cache fingerprint includes the DataLab extractor/schema version and stores usage metadata separately. Agent 0 was notified; its active v15 inference process and preserved v15 `code.zip` remain unchanged.

The patch here is generated against the preserved, clean-tested v15 `code.zip` for source files present in that archive; the root README change is against the checked-in base. Full candidate source files are included under repository-relative paths.

## Validation boundary

Focused mock tests passed 3/3; the full unit suite passed 117/117; Python compilation passed. No authenticated DataLab request, corpus extraction, or v16 sample/target evaluation was run because `DATALAB_API_KEY` is absent from process environment and local `.env`. Treat this as a mock/unit-verified candidate only. The existing `code.zip` does not include the DataLab module or dependency.