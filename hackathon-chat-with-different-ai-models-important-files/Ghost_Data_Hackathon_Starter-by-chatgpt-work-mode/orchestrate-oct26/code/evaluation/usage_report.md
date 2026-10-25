# Usage report — preparation template

No full-dataset inference run has occurred. This is not the final required report.

Record the run ID, source revision, output SHA-256, timestamp, provider/model names, calls, input/output/cached tokens, retries, failed calls, cache hits and misses, totals, average per request (518), pricing source/date, estimated total and per-request cost. Include per-model and overall tables. Specify whether extraction costs are included and distinguish cached reusable extraction from newly billed calls. Do not report unavailable token counts as zero.

Use provider-reported usage for each call; account for retries and image tokens where available. Record prices as configuration, with a verified pricing source. Formula: sum(input_tokens * input_price_per_million + output_tokens * output_price_per_million)/1,000,000; apply separate cached-input rates when appropriate.

Development coding-assistant use and final audit-agent inference are different activities. This report must describe the final full-dataset run that generated output.csv.
