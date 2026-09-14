"""Serializable domain types for the local control core."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class TaskStatus(StrEnum):
    WAITING_APPROVAL = "waiting_approval"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    task_id: str
    title: str
    actions: list[str]
    status: TaskStatus
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    approval_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Task":
        return cls(
            task_id=str(value["task_id"]),
            title=str(value["title"]),
            actions=[str(action) for action in value.get("actions", [])],
            status=TaskStatus(value["status"]),
            created_at=str(value["created_at"]),
            updated_at=str(value["updated_at"]),
            approval_note=value.get("approval_note"),
        )


@dataclass
class AuditEvent:
    event_id: str
    task_id: str
    event_type: str
    occurred_at: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "AuditEvent":
        return cls(
            event_id=str(value["event_id"]),
            task_id=str(value["task_id"]),
            event_type=str(value["event_type"]),
            occurred_at=str(value["occurred_at"]),
            payload=dict(value.get("payload", {})),
            previous_hash=str(value["previous_hash"]),
            event_hash=str(value["event_hash"]),
        )
