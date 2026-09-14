# MetaForge Core

MetaForge Core is a small, local-first task control core for coding agents. It
does not execute an LLM or automate deployment by itself. Instead, it gives an
agent host a deterministic place to record tasks, apply a narrow approval
policy, and retain a tamper-evident audit trail.

The public reference implementation intentionally focuses on the control
boundary:

- local JSON state with atomic writes
- explicit task lifecycle transitions
- approval gates for risky actions such as `git.push` and `deploy`
- hash-linked audit events that can be verified offline
- a small optional FastAPI surface and CLI demo

It is an alpha reference implementation, not a hosted service and not a claim
of unattended autonomy. Production users must supply their own identity,
authorization, isolation, secret management, persistence, and operational
controls.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m pip install -e .
metaforge demo
python -m unittest discover -s tests -v
```

The demo writes only to `.metaforge/demo-state.json`, which is ignored by Git.

To expose the optional local API:

```bash
metaforge serve --host 127.0.0.1 --port 8787
```

Create a task with a guarded action:

```bash
curl -X POST http://127.0.0.1:8787/v1/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Release package","actions":["git.push"]}'
```

The task starts in `waiting_approval`. Approve it through
`POST /v1/tasks/{task_id}/approve`, then transition it through `ready`,
`running`, and a terminal status.

## Safety model

The built-in policy is deliberately small. It requires approval for
`git.push`, `deploy`, `shell.destructive`, `network.egress`, and
`credential.use`. The policy does not grant operating-system permissions, and
approval records are not an authorization system. Integrators must enforce
real permissions below this interface.

The audit chain detects accidental or unsophisticated edits to the persisted
event history. It is not a substitute for signed, external, append-only audit
storage.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Local health check |
| `POST` | `/v1/tasks` | Create a task |
| `GET` | `/v1/tasks/{task_id}` | Read task state |
| `POST` | `/v1/tasks/{task_id}/approve` | Record an approval |
| `POST` | `/v1/tasks/{task_id}/transition` | Apply an allowed transition |
| `GET` | `/v1/audit/verify` | Verify the local audit chain |

Set `METAFORGE_STATE_PATH` to put local state somewhere other than the default
`.metaforge/state.json`.

## Development

```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
[SECURITY.md](SECURITY.md) before opening an issue or pull request.

## License

[MIT](LICENSE)
