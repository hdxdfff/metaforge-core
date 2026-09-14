"""Atomic JSON persistence for local demonstrations and single-user tooling."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonTaskStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": 1, "tasks": {}, "events": []}
        with self.path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if value.get("schema_version") != 1:
            raise ValueError("unsupported state schema")
        return value

    def write(self, value: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)
