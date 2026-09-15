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

1. Run a deeper secret scan with the release maintainer's chosen scanner.
2. Verify CI on the target GitHub repository.
3. Review the public README and project name with the maintainer.
4. Create the public remote only after those checks pass.

## Local verification completed

A fresh local clone of the candidate compiled successfully, ran all five unit
tests, passed the same basic pattern scan, and completed `git fsck --full`
without errors. This is not a substitute for a dedicated secret scanner or
GitHub-hosted CI.

The final local pass also scanned every tracked file and every reachable Git
commit for common cloud/API token, private-key, credential-file, and
high-risk assignment patterns. It reported no findings without printing file
contents.
