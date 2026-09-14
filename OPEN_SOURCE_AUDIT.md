# Open-source preparation record

## Included in this candidate

- A new, standalone reference implementation under `src/metaforge_core/`.
- Unit tests, a local-only CLI, optional FastAPI API, CI, contribution and
  security guidance, and an MIT license.
- No source history was copied from the private MetaForge repository.

## Explicitly excluded

- Private repository history, operator notes, prompts, goals, memory, and
  machine-specific launch scripts.
- Runtime state, logs, generated reports, cache directories, binaries,
  credentials, `.env`, third-party service checkouts, and desktop packaging.
- Deployment, payment, customer, and hosted-service claims.

## Release gate still required

1. Run a repository secret scan in a clean clone.
2. Verify CI on the target GitHub repository.
3. Review the public README and project name with the maintainer.
4. Create the public remote only after those checks pass.
