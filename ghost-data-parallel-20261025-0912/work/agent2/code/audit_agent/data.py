from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(32 * 1024 * 1024)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"{path}: missing or duplicate header")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(f"{path}: malformed CSV record")
        return rows


def parse_instant(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            raise ValueError("timestamp is empty")
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a timezone: {value!r}")
    return parsed


def maybe_instant(value: Any) -> datetime | None:
    if value is None or not str(value).strip():
        return None
    try:
        return parse_instant(value)
    except (TypeError, ValueError):
        return None


def path_is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
