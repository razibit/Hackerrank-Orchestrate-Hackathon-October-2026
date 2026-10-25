# Inference usage report

## Provider and metering

- Provider: Microsoft Foundry, using the Azure OpenAI-compatible interface.
- Model and deployment: openai--gpt-oss-120b.
- Provisioning observed for the run: two A100 accelerators.
- Authentication: Azure CLI Entra identity; no API key is included in source or this report.
- The user authorized open-ended Foundry GPU hours and did not impose a model-call or token quota. The agent still processes a finite supplied dataset and uses bounded per-call retry behavior.
- The user reports a rate of USD $7 per hour and 10–20 hours of available credits. Azure did not provide a verifiable billable rate, billing start, or whether the rate applies per A100 or to the deployment. The estimates below are scenarios only, not invoiced or provider-verified cost.
- Prompt/completion tokens are provider-reported. The deterministic extraction layer makes no hidden model calls.

## Final target processing

No complete target output file was produced because 256 of 518 cases remained unresolved. The source code correctly withheld output.csv. Accordingly, these are the measured final target-processing totals, not usage for a successful CSV submission.

| Measurement | Final cumulative target processing |
|---|---:|
| Target requests processed | 518 |
| Provider attempts, including retry/failure | 712 |
| Successful provider attempts | 711 |
| Failed attempts | 1 |
| Retries | 1 |
| Input tokens | 1,765,441 |
| Output tokens | 799,581 |
| Total tokens | 2,565,022 |
| Average total tokens per target request | 4,952 |
| Instrumented elapsed time across target v4 and v5 | 6,146.985 seconds (1.7075 hours) |
| Accelerator-equivalent time at two A100s | 3.414690 accelerator-hours |
| Final replay cache accounting | 678 cached results reused; 33 new policy-resolution calls |
| Provider-reported USD cost | Unavailable |

The first target pass recorded 679 attempts, 678 successes, one failed attempt and one retry; it used 2,539,583 tokens over 6,001.750 seconds. The final replay reused 678 cached results and made 33 additional successful policy-condition calls, adding 25,439 tokens over 145.235 seconds. Cumulative totals above avoid counting cached results as new provider calls. The one failed attempt and retry occurred in the initial target pass.

At the user-reported USD $7/hour rate, the target's instrumented elapsed time corresponds to about USD $11.95 total (USD $0.0231 per request) if the rate covers the whole deployment-hour, or about USD $23.90 total (USD $0.0462 per request) if it applies per A100 accelerator-hour. These conditional scenarios exclude any time before/after the measured program runtime and cannot confirm actual billing or credit consumption.

## Public sample and independent custom cases

| Run | Results | New model calls in the final replay/run | Tokens represented by the completed inference artifact | Instrumented elapsed |
|---|---|---:|---:|---:|
| Sample final inference and v7 replay | 16/32 resolved; 16 blocked | Final inference made 1 new call and reused 40 responses; final-source cache-only replay reused 41 responses and made zero new calls | 100,340 input + 49,275 output = 149,615 total across the 41 unique responses used by this sample artifact | 7.625 seconds for the final inference replay; cache-only replay made no provider calls |
| Three custom synthetic cases | 3/3 validated | 3 successful calls; no retry/failure | 5,227 input + 1,983 output = 7,210 total | 21.172 seconds instrumented; 22.202 seconds observed CLI wall time; 0.011649 accelerator-hours |

The final sample artifact includes 40 response-cache entries from the preceding sample iteration and one additional model response (797 tokens). The 149,615-token total describes the unique responses used to create the artifact, not tokens newly billed during the final replay. Sample metrics cover resolved rows only and are selection-biased.

## Cost and measurement limitations

Azure returned no USD cost value for these runs. Accelerator-equivalent hours are elapsed runtime multiplied by the configured accelerator count; they do not measure provider billable uptime. The user's rate and credit balance were not independently verifiable, and their billing unit is unknown. No per-token price was assumed. Earlier exploratory iterations are recorded in the challenge log and are not added to the final target-processing totals above.

There is no complete target CSV, so there is no output checksum or claim of complete target evaluation. The output release gate remains blocked by the unresolved evidence described in evaluation_report.md.

## Fresh-package no-inference replay

The final archive was extracted into a fresh directory, dependencies were installed into a new Python 3.12.5 virtual environment, external-dataset preflight passed, and all 65 tests passed. Its full 518-request cache-only replay reused 711 cached responses with zero misses and zero new provider calls. It reproduced 262 resolved and 256 unresolved cases, and withheld output.csv as designed. The replay usage checkpoint carries 712 historical attempt records from the cached inference history; these were not new calls.
