"""Task lifecycle service with approval gates and a hash-linked event ledger."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import replace
from typing import Any

from .models import AuditEvent, Task, TaskStatus, utc_now
from .policy import ActionPolicy
from .store import JsonTaskStore


ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.WAITING_APPROVAL: frozenset({TaskStatus.CANCELLED}),
    TaskStatus.READY: frozenset({TaskStatus.RUNNING, TaskStatus.CANCELLED}),
    TaskStatus.RUNNING: frozenset({TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}),
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.FAILED: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
}
GENESIS_HASH = "0" * 64


class TaskNotFoundError(KeyError):
    pass


class InvalidTransitionError(ValueError):
    pass


class TaskService:
    def __init__(self, store: JsonTaskStore, policy: ActionPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or ActionPolicy()

    def create_task(self, title: str, actions: list[str] | None = None) -> Task:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("title must not be empty")
        clean_actions = sorted({action.strip() for action in actions or [] if action.strip()})
        decision = self.policy.decide(clean_actions)
        status = TaskStatus.WAITING_APPROVAL if decision.requires_approval else TaskStatus.READY
        task = Task(task_id=str(uuid.uuid4()), title=clean_title, actions=clean_actions, status=status)
        state = self.store.read()
        state["tasks"][task.task_id] = task.to_dict()
        self._append_event(
            state,
            task.task_id,
            "task.created",
            {"actions": clean_actions, "status": status.value, "guarded_actions": decision.guarded_actions},
        )
        self.store.write(state)
        return task

    def get_task(self, task_id: str) -> Task:
        state = self.store.read()
        try:
            return Task.from_dict(state["tasks"][task_id])
        except KeyError as error:
            raise TaskNotFoundError(task_id) from error

    def approve_task(self, task_id: str, note: str = "") -> Task:
        state = self.store.read()
        task = self._task_from_state(state, task_id)
        if task.status is not TaskStatus.WAITING_APPROVAL:
            raise InvalidTransitionError("only waiting_approval tasks can be approved")
        updated = replace(task, status=TaskStatus.READY, updated_at=utc_now(), approval_note=note.strip() or None)
        state["tasks"][task_id] = updated.to_dict()
        self._append_event(state, task_id, "task.approved", {"note": updated.approval_note})
        self.store.write(state)
        return updated

    def transition_task(self, task_id: str, target_status: TaskStatus) -> Task:
        state = self.store.read()
        task = self._task_from_state(state, task_id)
        if target_status not in ALLOWED_TRANSITIONS[task.status]:
            raise InvalidTransitionError(f"cannot transition {task.status.value} to {target_status.value}")
        updated = replace(task, status=target_status, updated_at=utc_now())
        state["tasks"][task_id] = updated.to_dict()
        self._append_event(state, task_id, "task.transitioned", {"status": target_status.value})
        self.store.write(state)
        return updated

    def verify_audit_chain(self) -> bool:
        state = self.store.read()
        previous_hash = GENESIS_HASH
        for raw_event in state["events"]:
            event = AuditEvent.from_dict(raw_event)
            if event.previous_hash != previous_hash:
                return False
            if event.event_hash != self._hash_event(event):
                return False
            previous_hash = event.event_hash
        return True

    @staticmethod
    def _task_from_state(state: dict[str, Any], task_id: str) -> Task:
        try:
            return Task.from_dict(state["tasks"][task_id])
        except KeyError as error:
            raise TaskNotFoundError(task_id) from error

    def _append_event(self, state: dict[str, Any], task_id: str, event_type: str, payload: dict[str, Any]) -> None:
        previous_hash = state["events"][-1]["event_hash"] if state["events"] else GENESIS_HASH
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            task_id=task_id,
            event_type=event_type,
            occurred_at=utc_now(),
            payload=payload,
            previous_hash=previous_hash,
            event_hash="",
        )
        event.event_hash = self._hash_event(event)
        state["events"].append(event.to_dict())

    @staticmethod
    def _hash_event(event: AuditEvent) -> str:
        material = {
            "event_id": event.event_id,
            "task_id": event.task_id,
            "event_type": event.event_type,
            "occurred_at": event.occurred_at,
            "payload": event.payload,
            "previous_hash": event.previous_hash,
        }
        encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
