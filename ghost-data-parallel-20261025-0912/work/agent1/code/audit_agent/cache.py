from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from dataclasses import asdict

from .data import parse_instant, read_csv
from .extractors import extract_activity, extract_sources
from .model import ModelCallError
from .types import Observation


def canonical_hash(value: Any) -> str:
    serialized = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class JsonResponseCache:
    """Content-addressed cache whose keys include model, prompt and schema inputs."""

    version = "foundry-json-response-v2"

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0
        self.reused_usage: dict[str, dict[str, Any]] = {}

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        if not path.is_file():
            self.misses += 1
            return None
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            if item.get("cache_version") != self.version or item.get("key") != key:
                raise ValueError("cache version/key mismatch")
            response = item.get("response")
            if not isinstance(response, dict):
                raise ValueError("cached response is not an object")
        except (OSError, ValueError, json.JSONDecodeError):
            self.misses += 1
            return None
        self.hits += 1
        usage = item.get("usage_records", [])
        if isinstance(usage, list):
            self.reused_usage[key] = {"records": usage}
        return response

    def put(self, key: str, response: dict[str, Any], usage_records: list[dict[str, Any]]) -> None:
        path = self._path(key)
        temp = path.with_suffix(".tmp")
        data = {"cache_version": self.version, "key": key, "response": response, "usage_records": usage_records}
        temp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        temp.replace(path)


class CachedChatModel:
    """Cache wrapper that exposes only current, validated request inputs to the provider."""

    def __init__(self, model: Any, cache: JsonResponseCache, cache_only: bool = False):
        self.model = model
        self.cache = cache
        self.cache_only = cache_only

    @property
    def provider(self) -> str:
        return self.model.provider

    @property
    def model_name(self) -> str:
        return self.model.model

    @property
    def deployment(self) -> str:
        return self.model.deployment

    def chat_json(self, purpose: str, system_prompt: str, payload: Any, schema: dict[str, Any], max_tokens: int = 3000) -> dict[str, Any]:
        key = canonical_hash({
            "cache_version": self.cache.version,
            "provider": self.provider,
            "model": self.model_name,
            "deployment": self.deployment,
            "purpose": purpose,
            "system_prompt": system_prompt,
            "payload": payload,
            "schema": schema,
            "max_tokens": max_tokens,
        })
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        if self.cache_only:
            raise ModelCallError("cache-only replay stopped because a response was not cached")
        start = len(self.model.ledger.records)
        result = self.model.chat_json(purpose, system_prompt, payload, schema, max_tokens)
        self.cache.put(key, result, self.model.ledger.records[start:])
        return result


def dataset_fingerprint(dataset: Path) -> str:
    files = [
        (dataset / name).resolve() for name in (
            "deletion_requests.csv", "sample_deletion_requests.csv", "user_identities.csv",
            "user_audit_log.csv", "system_activity.csv", "deletion_rules.csv", "evidence_files.csv",
        ) if (dataset / name).is_file()
    ]
    for row in read_csv(dataset / "evidence_files.csv"):
        files.append((dataset / row["file_path"]).resolve())
    digest = hashlib.sha256(b"evidence-extractor-v3\0")
    for source_file in (
        Path(__file__).with_name("extractors.py"),
        Path(__file__).with_name("data.py"),
        Path(__file__).with_name("types.py"),
    ):
        digest.update(source_file.name.encode("utf-8"))
        digest.update(source_file.read_bytes())
    for path in sorted(set(files), key=lambda item: str(item).casefold()):
        if not path.is_file():
            raise FileNotFoundError(f"dataset input is missing: {path.name}")
        digest.update(str(path.relative_to(dataset.resolve())).replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest()


def load_or_extract(dataset: Path, cache_root: Path) -> tuple[list[Observation], list[Observation], bool, str]:
    fingerprint = dataset_fingerprint(dataset)
    cache_dir = cache_root / "extract" / fingerprint
    source_path = cache_dir / "sources.jsonl"
    activity_path = cache_dir / "activity.jsonl"
    if source_path.is_file() and activity_path.is_file():
        try:
            sources = [_observation_from_json(line) for line in source_path.read_text(encoding="utf-8").splitlines() if line]
            activity = [_observation_from_json(line) for line in activity_path.read_text(encoding="utf-8").splitlines() if line]
            return sources, activity, True, fingerprint
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            pass
    sources = extract_sources(dataset)
    activity = extract_activity(dataset)
    cache_dir.mkdir(parents=True, exist_ok=True)
    for path, values in ((source_path, sources), (activity_path, activity)):
        temp = path.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8", newline="\n") as stream:
            for value in values:
                item = asdict(value)
                item["available_at"] = value.available_at.isoformat()
                item["observed_at"] = value.observed_at.isoformat()
                stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":"), default=str) + "\n")
        temp.replace(path)
    return sources, activity, False, fingerprint


def _observation_from_json(line: str) -> Observation:
    item = json.loads(line)
    item["available_at"] = parse_instant(item["available_at"])
    item["observed_at"] = parse_instant(item["observed_at"])
    return Observation(**item)
