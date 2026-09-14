"""Small command-line entry point for local evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .models import TaskStatus
from .service import TaskService
from .store import JsonTaskStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metaforge")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="run a local, approval-gated demonstration")
    demo.add_argument("--state", type=Path, default=Path(".metaforge/demo-state.json"))
    serve = subcommands.add_parser("serve", help="run the optional local HTTP API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8787)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "demo":
        service = TaskService(JsonTaskStore(args.state))
        task = service.create_task("Publish a release", ["git.push"])
        print(f"created {task.task_id}: {task.status.value}")
        task = service.approve_task(task.task_id, "local demo approval")
        task = service.transition_task(task.task_id, TaskStatus.RUNNING)
        task = service.transition_task(task.task_id, TaskStatus.COMPLETED)
        print(f"completed {task.task_id}: audit_valid={service.verify_audit_chain()}")
        return
    from uvicorn import run

    from .api import create_app

    run(create_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
