from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .data import parse_instant


class ModelConfigurationError(RuntimeError):
    pass


class RunBudgetExceeded(RuntimeError):
    pass


class ModelCallError(RuntimeError):
    pass


class OutputTruncatedError(ModelCallError):
    """The provider stopped a structured response at its output-token limit."""




def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ModelConfigurationError(f"Required environment variable {name} is not set")
    return value


def _openai_v1_base(endpoint: str) -> str:
    """Normalize either a Foundry base endpoint or its copied completion URL."""
    parts = urlsplit(endpoint.strip())
    if parts.scheme != "https" or not parts.netloc:
        raise ModelConfigurationError("AZURE_FOUNDRY_ENDPOINT must be an HTTPS URL")
    path = parts.path.rstrip("/")
    completion_suffix = "/chat/completions"
    if path.endswith("/openai/v1" + completion_suffix):
        path = path[:-len(completion_suffix)]
    elif path.endswith("/openai/v1"):
        pass
    elif not path:
        path = "/openai/v1"
    else:
        raise ModelConfigurationError(
            "AZURE_FOUNDRY_ENDPOINT must be a resource URL, /openai/v1 URL, or chat-completions URL"
        )
    return urlunsplit((parts.scheme, parts.netloc, path + "/", "", ""))


class AzureCliTokenProvider:
    """Gets a short-lived Entra token without displaying or persisting it."""

    def __call__(self) -> str:
        arguments = [
            "account", "get-access-token", "--scope", "https://ai.azure.com/.default",
            "--query", "accessToken", "--output", "tsv", "--only-show-errors",
        ]
        # On Windows Azure CLI is commonly installed as az.cmd. subprocess
        # cannot execute .cmd files directly, so ask cmd.exe to resolve it.
        command = ["cmd.exe", "/d", "/c", "az", *arguments] if os.name == "nt" else ["az", *arguments]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        if result.returncode != 0 or not result.stdout.strip():
            raise ModelConfigurationError("Azure CLI could not obtain an Entra token for Microsoft Foundry")
        return result.stdout.strip()


@dataclass
class UsageLedger:
    records: list[dict[str, Any]]

    @classmethod
    def create(cls) -> "UsageLedger":
        return cls([])

    def add(self, record: dict[str, Any]) -> None:
        self.records.append(record)

    def totals(self) -> dict[str, Any]:
        successful = [row for row in self.records if row.get("success")]
        return {
            "api_calls": len(self.records),
            "successful_calls": len(successful),
            "failed_calls": len(self.records) - len(successful),
            "retries": sum(max(0, int(row.get("attempt", 1)) - 1) for row in self.records),
            "input_tokens": sum(int(row.get("input_tokens") or 0) for row in self.records),
            "output_tokens": sum(int(row.get("output_tokens") or 0) for row in self.records),
            "total_tokens": sum(int(row.get("total_tokens") or 0) for row in self.records),
            "call_records": self.records,
        }


class FoundryChatModel:
    """Stateless structured chat calls to an existing Foundry OpenAI-compatible deployment."""

    def __init__(self, ledger: UsageLedger, max_calls: int | None = None):
        endpoint = (
            os.environ.get("AZURE_FOUNDRY_ENDPOINT", "").strip()
            or os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
        )
        if not endpoint:
            raise ModelConfigurationError("Required environment variable AZURE_FOUNDRY_ENDPOINT is not set")
        deployment = (
            os.environ.get("AZURE_FOUNDRY_DEPLOYMENT", "").strip()
            or os.environ.get("DEPLOYMENT_NAME", "").strip()
        )
        if not deployment:
            raise ModelConfigurationError("Required environment variable AZURE_FOUNDRY_DEPLOYMENT is not set")

        uncapped = os.environ.get("AZURE_FOUNDRY_ALLOW_UNCAPPED_GPU_HOURS", "").strip() == "1"
        cap_text = os.environ.get("MAX_RUN_COST_USD", "30").strip()
        if uncapped:
            cap: float | None = None
        else:
            try:
                cap = float(cap_text)
            except ValueError:
                raise ModelConfigurationError("MAX_RUN_COST_USD must be a positive number") from None
            if cap <= 0:
                raise ModelConfigurationError("MAX_RUN_COST_USD must be greater than zero")

        rate_text = os.environ.get("AZURE_FOUNDRY_HOURLY_USD_PER_ACCELERATOR", "").strip()
        try:
            hourly_rate: float | None = float(rate_text) if rate_text else None
            accelerator_count = int(os.environ.get("AZURE_FOUNDRY_ACCELERATOR_COUNT", "1"))
        except ValueError:
            raise ModelConfigurationError("Foundry accelerator rate/count configuration is invalid") from None
        billing_text = os.environ.get("AZURE_FOUNDRY_BILLING_START_UTC", "").strip()
        billing_started = parse_instant(billing_text) if billing_text else None
        if accelerator_count <= 0 or (hourly_rate is not None and hourly_rate <= 0):
            raise ModelConfigurationError("Foundry hourly rate and accelerator count must be positive")
        if not uncapped and (hourly_rate is None or billing_started is None):
            raise ModelConfigurationError(
                "A verified Foundry accelerator rate and billing start are required to enforce MAX_RUN_COST_USD; "
                "use --allow-uncapped-gpu-hours only when explicitly authorized"
            )

        self.endpoint = _openai_v1_base(endpoint)
        self.api_key = os.environ.get("AZURE_FOUNDRY_API_KEY", "").strip()
        self.token_provider = None if self.api_key else AzureCliTokenProvider()
        self.deployment = deployment
        self.provider = "Microsoft Foundry"
        self.model = (
            os.environ.get("AZURE_FOUNDRY_MODEL_NAME", "").strip()
            or os.environ.get("MODEL_NAME", "").strip()
            or deployment
        )
        self.rate = hourly_rate
        self.accelerators = accelerator_count
        self.billing_started = billing_started
        self.cap = cap
        self.uncapped_gpu_hours = uncapped
        self.tracking_started = datetime.now(timezone.utc)
        if max_calls is None:
            configured_calls = os.environ.get("MAX_MODEL_CALLS", "0").strip() or "0"
            try:
                max_calls = int(configured_calls)
            except ValueError:
                raise ModelConfigurationError("MAX_MODEL_CALLS must be a non-negative integer") from None
        if max_calls < 0:
            raise ModelConfigurationError("MAX_MODEL_CALLS must be zero (unlimited) or a positive integer")
        # Zero means no request-count cap. The caller can still stop the run, and
        # each individual provider request retains bounded retries.
        self.max_calls = max_calls
        self.ledger = ledger

    def _gpu_hours(self, at: datetime | None = None) -> float:
        now = at or datetime.now(timezone.utc)
        start = self.billing_started or self.tracking_started
        elapsed_hours = max(0.0, (now - start).total_seconds() / 3600)
        return elapsed_hours * self.accelerators

    def _estimated_cost(self, at: datetime | None = None) -> float | None:
        if self.rate is None or self.billing_started is None:
            return None
        return self._gpu_hours(at) * self.rate

    def _guard(self) -> None:
        if self.max_calls and len(self.ledger.records) >= self.max_calls:
            raise RunBudgetExceeded("MAX_MODEL_CALLS has been reached")
        estimate = self._estimated_cost()
        if self.cap is not None and estimate is not None and estimate >= self.cap:
            raise RunBudgetExceeded(
                f"Foundry managed-compute estimate reached the authorized ${self.cap:.2f} cap"
            )

    def chat_json(self, purpose: str, system_prompt: str, payload: Any, schema: dict[str, Any], max_tokens: int = 3000) -> dict[str, Any]:
        self._guard()
        try:
            from openai import OpenAI
        except ImportError:
            raise ModelConfigurationError("Install code/requirements.txt before runtime inference") from None
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))},
        ]
        last_error: Exception | None = None
        for attempt in range(1, 4):
            self._guard()
            started = time.monotonic()
            record: dict[str, Any] = {
                "purpose": purpose,
                "provider": self.provider,
                "model": self.model,
                "deployment": self.deployment,
                "attempt": attempt,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "request_sent": False,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
            }
            try:
                # The OpenAI SDK's api_key option is a string; refresh short-lived
                # Entra tokens per request instead of passing a callable as a key.
                api_key = self.api_key or self.token_provider()
                client = OpenAI(
                    base_url=self.endpoint,
                    api_key=api_key,
                    timeout=90.0,
                    max_retries=0,
                )
                record["request_sent"] = True
                response = client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    temperature=0,
                    max_tokens=max_tokens,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {"name": f"{purpose}_result", "strict": True, "schema": schema},
                    },
                )
                content = response.choices[0].message.content or ""
                usage = response.usage
                if usage:
                    record["input_tokens"] = usage.prompt_tokens
                    record["output_tokens"] = usage.completion_tokens
                    record["total_tokens"] = usage.total_tokens
                choice = response.choices[0]
                record["finish_reason"] = choice.finish_reason
                record["response_content_length"] = len(content)
                if choice.finish_reason == "length":
                    raise OutputTruncatedError("Foundry stopped the structured response at its output-token limit")
                stripped = content.lstrip()
                record["response_content_kind"] = (
                    "empty" if not stripped else
                    "json_object" if stripped.startswith("{") else
                    "json_array" if stripped.startswith("[") else
                    "markdown_fence" if stripped.startswith("```") else
                    "other_text"
                )
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as exc:
                    record["json_error_position"] = exc.pos
                    record["json_error_category"] = exc.msg[:80]
                    raise
                record["success"] = True
                record["response_model"] = getattr(response, "model", self.model)
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                record["finished_at"] = datetime.now(timezone.utc).isoformat()
                estimate = self._estimated_cost()
                record["estimated_total_compute_cost_usd"] = round(estimate, 6) if estimate is not None else None
                elapsed_hours = max(0.0, (datetime.now(timezone.utc) - self.tracking_started).total_seconds() / 3600)
                record["accelerator_equivalent_hours_since_run_start"] = round(elapsed_hours * self.accelerators, 6)
                record["gpu_hours_since_billing_start"] = round(self._gpu_hours(), 6) if self.billing_started else None
                self.ledger.add(record)
                if self.cap is not None and estimate is not None and estimate >= self.cap:
                    raise RunBudgetExceeded(
                        f"Foundry managed-compute estimate reached the authorized ${self.cap:.2f} cap"
                    )
                return data
            except RunBudgetExceeded:
                raise
            except OutputTruncatedError as exc:
                last_error = exc
                record["error_type"] = type(exc).__name__
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                record["finished_at"] = datetime.now(timezone.utc).isoformat()
                self.ledger.add(record)
                raise
            except Exception as exc:  # bounded retry; logs contain type only, never request or key
                last_error = exc
                record["error_type"] = type(exc).__name__
                record["elapsed_seconds"] = round(time.monotonic() - started, 3)
                record["finished_at"] = datetime.now(timezone.utc).isoformat()
                self.ledger.add(record)
                if attempt == 3:
                    break
                time.sleep(0.5 * (2 ** (attempt - 1)))
        raise ModelCallError(f"Foundry structured call failed after bounded retries ({type(last_error).__name__})") from None


INTENT_SCHEMA = {
    "type": "object",
    "properties": {"cases": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "case_id": {"type": "string"},
            "intent": {"type": "string", "enum": ["DELETE", "NOT_DELETE", "UNRESOLVED"]},
            "confidence": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
            "reason": {"type": "string"},
        },
        "required": ["case_id", "intent", "confidence", "reason"],
        "additionalProperties": False,
    }}},
    "required": ["cases"],
    "additionalProperties": False,
}


OBSERVATION_SCHEMA = {
    "type": "object",
    "properties": {"observations": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "observation_id": {"type": "string"},
            "system_id": {"type": "string"},
            "resource_id": {"type": "string"},
            "relevant_to_subject": {"type": "string", "enum": ["YES", "NO", "UNRESOLVED"]},
            "category": {"type": "string", "enum": [
                "USER_PROFILE", "SECONDARY_IDENTIFIER", "SEARCH_INDEX_ENTRY", "CACHE_ENTRY",
                "SUPPORT_MESSAGE", "SUPPORT_ATTACHMENT", "ANALYTICS_PROFILE", "PRODUCT_TELEMETRY",
                "USER_EXPORT", "MARKETING_PROFILE", "EMAIL_DELIVERY_LOG", "SECURITY_AUDIT_LOG",
                "LEGAL_HOLD_RECORD", "BACKUP_ARCHIVE", "ACCOUNT_TOMBSTONE", "DATA_FLOW", "UNRESOLVED",
            ]},
            "state": {"type": "string", "enum": ["PRESENT", "ABSENT", "ACTIVE", "DISABLED", "BLOCKED", "REDACTED", "ANONYMIZED", "UNKNOWN"]},
            "identifiers_exposed": {"type": "string", "enum": ["YES", "NO", "UNRESOLVED"]},
            "policy_condition": {"type": "string", "enum": ["TRUE", "FALSE", "UNRESOLVED", "NOT_APPLICABLE"]},
            "scope_complete": {"type": "string", "enum": ["TRUE", "FALSE", "UNRESOLVED", "NOT_APPLICABLE"]},
            "reason": {"type": "string"},
        },
        "required": ["observation_id", "system_id", "resource_id", "relevant_to_subject", "category", "state", "identifiers_exposed", "policy_condition", "scope_complete", "reason"],
        "additionalProperties": False,
    }}},
    "required": ["observations"],
    "additionalProperties": False,
}


POLICY_CONDITION_SCHEMA = {
    "type": "object",
    "properties": {"policy_conditions": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "observation_id": {"type": "string"},
            "condition": {"type": "string", "enum": ["TRUE", "FALSE", "UNRESOLVED"]},
            "reason": {"type": "string"},
        },
        "required": ["observation_id", "condition", "reason"],
        "additionalProperties": False,
    }}},
    "required": ["policy_conditions"],
    "additionalProperties": False,
}


def classify_intents(model: FoundryChatModel, requests: list[dict[str, str]], prompt: str, batch_size: int = 20) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for start in range(0, len(requests), batch_size):
        batch = requests[start:start + batch_size]
        result = model.chat_json(
            "intent_classification", prompt,
            {"requests": [{"case_id": r["case_id"], "request_text": r["request_text"]} for r in batch]},
            INTENT_SCHEMA, max_tokens=2500,
        )
        expected = {r["case_id"] for r in batch}
        returned = [item.get("case_id", "") for item in result.get("cases", [])]
        if set(returned) != expected or len(returned) != len(expected):
            raise ValueError("Intent response did not return exactly one result for every request in the batch")
        for item in result["cases"]:
            output[item["case_id"]] = item
    return output


def classify_policy_conditions(
    model: FoundryChatModel,
    case_id: str,
    audit_at: str,
    observations: list[dict[str, Any]],
    prompt: str,
    batch_size: int = 5,
) -> dict[str, dict[str, str]]:
    """Recheck only unresolved conditional policies with explicit record content."""
    output: dict[str, dict[str, str]] = {}
    for start in range(0, len(observations), batch_size):
        batch = observations[start:start + batch_size]
        result = model.chat_json(
            "policy_condition_resolution", prompt,
            {"case_id": case_id, "audit_at": audit_at, "observations": batch},
            POLICY_CONDITION_SCHEMA, max_tokens=1200,
        )
        expected = {str(item["observation_id"]) for item in batch}
        items = result.get("policy_conditions", [])
        returned = [str(item.get("observation_id", "")) for item in items]
        if set(returned) != expected or len(returned) != len(expected):
            raise ValueError(f"Policy-condition response omitted or invented observation IDs for {case_id}")
        for item in items:
            output[str(item["observation_id"])] = item
    return output


def classify_observations(
    model: FoundryChatModel,
    case_id: str,
    subject_id: str,
    cutoff: str,
    observations: list[dict[str, Any]],
    prompt: str,
    policy_rules: dict[str, dict[str, str]] | None = None,
    identity_context: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    def classify_batch(batch: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        try:
            result = model.chat_json(
                "evidence_classification", prompt,
                {
                    "case_id": case_id,
                    "subject_id": subject_id,
                    "identity_context": identity_context or {},
                    "audit_at": cutoff,
                    "policy_rules": policy_rules or {},
                    "observations": batch,
                },
                OBSERVATION_SCHEMA, max_tokens=2500,
            )
        except OutputTruncatedError:
            if len(batch) == 1:
                raise
            midpoint = len(batch) // 2
            return classify_batch(batch[:midpoint]) | classify_batch(batch[midpoint:])
        expected = {str(item["observation_id"]) for item in batch}
        items = result.get("observations", [])
        returned = [str(item.get("observation_id", "")) for item in items]
        if set(returned) != expected or len(returned) != len(expected):
            raise ValueError(f"Evidence response omitted or invented observation IDs for {case_id}")
        return {str(item["observation_id"]): item for item in items}

    # Five records keep outputs well below the Foundry deployment's observed
    # response ceiling. If a future record is unusually verbose, split only
    # that batch recursively after a provider-reported length stop.
    for start in range(0, len(observations), 5):
        output.update(classify_batch(observations[start:start + 5]))
    return output
