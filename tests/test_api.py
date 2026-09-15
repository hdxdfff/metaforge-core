import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from metaforge_core.api import create_app


class ApiTests(unittest.TestCase):
    def test_guarded_task_approval_and_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            client = TestClient(create_app(Path(directory) / "state.json"))
            created = client.post(
                "/v1/tasks", json={"title": "Release", "actions": ["git.push"]}
            )
            self.assertEqual(created.status_code, 201)
            task_id = created.json()["task_id"]
            self.assertEqual(created.json()["status"], "waiting_approval")
            self.assertEqual(
                client.post(f"/v1/tasks/{task_id}/approve", json={"note": "reviewed"}).status_code,
                200,
            )
            self.assertEqual(
                client.post(f"/v1/tasks/{task_id}/transition", json={"status": "running"}).status_code,
                200,
            )
            completed = client.post(f"/v1/tasks/{task_id}/transition", json={"status": "completed"})
            self.assertEqual(completed.status_code, 200)
            self.assertEqual(completed.json()["status"], "completed")
            self.assertEqual(client.get("/v1/audit/verify").json(), {"valid": True})
