"""Optional HTTP wrapper; core policy and state remain local and explicit."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .models import TaskStatus
from .service import InvalidTransitionError, TaskNotFoundError, TaskService
from .store import JsonTaskStore


def create_app(state_path: str | Path | None = None) -> Any:
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as error:
        raise RuntimeError("Install MetaForge Core with its HTTP dependencies to use the API.") from error

    path = Path(state_path or os.environ.get("METAFORGE_STATE_PATH", ".metaforge/state.json"))
    service = TaskService(JsonTaskStore(path))
    app = FastAPI(title="MetaForge Core", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/tasks", status_code=201)
    def create_task(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return service.create_task(str(payload.get("title", "")), list(payload.get("actions", []))).to_dict()
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/v1/tasks/{task_id}")
    def get_task(task_id: str) -> dict[str, Any]:
        try:
            return service.get_task(task_id).to_dict()
        except TaskNotFoundError as error:
            raise HTTPException(status_code=404, detail="task not found") from error

    @app.post("/v1/tasks/{task_id}/approve")
    def approve_task(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return service.approve_task(task_id, str(payload.get("note", ""))).to_dict()
        except TaskNotFoundError as error:
            raise HTTPException(status_code=404, detail="task not found") from error
        except InvalidTransitionError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.post("/v1/tasks/{task_id}/transition")
    def transition_task(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            status = TaskStatus(str(payload.get("status", "")))
            return service.transition_task(task_id, status).to_dict()
        except TaskNotFoundError as error:
            raise HTTPException(status_code=404, detail="task not found") from error
        except (InvalidTransitionError, ValueError) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.get("/v1/audit/verify")
    def verify_audit() -> dict[str, bool]:
        return {"valid": service.verify_audit_chain()}

    return app
