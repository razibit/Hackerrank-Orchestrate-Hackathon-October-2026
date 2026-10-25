# Local setup notes

DataLab's documented highest-accuracy structured extraction mode is `accurate` (not `balanced`). SDK manages the underlying model selection and does not expose a fixed model ID in the result. See:
- https://documentation.datalab.to/docs/welcome/quickstart
- https://documentation.datalab.to/docs/recipes/structured-extraction/balanced-mode
- https://documentation.datalab.to/api-reference/extract-structured-data

Install pinned dependencies in the intended isolated environment. Set a rotated key interactively in the same PowerShell window that will launch extraction:

```powershell
$secret = Read-Host "DataLab API key (rotated)" -AsSecureString
$env:DATALAB_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
```

The pasted key is already present in chat; revoke/rotate it before live use. This keeps its replacement out of the source tree, logs, and command text. Keep the active v15 process/package untouched; run any live smoke only in a separate candidate process.