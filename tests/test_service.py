import json
import tempfile
import unittest
from pathlib import Path

from metaforge_core.models import TaskStatus
from metaforge_core.service import InvalidTransitionError, TaskService
from metaforge_core.store import JsonTaskStore


def make_service(directory: str) -> tuple[TaskService, Path]:
    path = Path(directory) / "state.json"
    return TaskService(JsonTaskStore(path)), path


class TaskServiceTests(unittest.TestCase):
    def test_guarded_task_needs_approval_and_keeps_a_valid_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, _ = make_service(directory)
            task = service.create_task("Ship", ["git.push"])
            self.assertIs(task.status, TaskStatus.WAITING_APPROVAL)
            task = service.approve_task(task.task_id, "reviewed")
            task = service.transition_task(task.task_id, TaskStatus.RUNNING)
            task = service.transition_task(task.task_id, TaskStatus.COMPLETED)
            self.assertIs(task.status, TaskStatus.COMPLETED)
            self.assertTrue(service.verify_audit_chain())

    def test_invalid_transition_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, _ = make_service(directory)
            task = service.create_task("Run checks", ["test.run"])
            with self.assertRaises(InvalidTransitionError):
                service.transition_task(task.task_id, TaskStatus.COMPLETED)

    def test_tampered_event_breaks_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service, path = make_service(directory)
            service.create_task("Run checks", ["test.run"])
            state = json.loads(path.read_text(encoding="utf-8"))
            state["events"][0]["payload"]["status"] = "completed"
            path.write_text(json.dumps(state), encoding="utf-8")
            self.assertFalse(service.verify_audit_chain())
