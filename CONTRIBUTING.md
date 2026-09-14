# Contributing

Thank you for improving MetaForge Core.

Before proposing a change, keep the project boundary intact: this repository
is a small, local reference control core. Do not add credentials, production
configuration, customer data, generated runtime state, packaged binaries, or
vendor source trees.

For each pull request:

1. Keep the behavior deterministic and local by default.
2. Add or update a `unittest` case for behavior changes.
3. Run `python -m compileall -q src tests` and
   `python -m unittest discover -s tests -v`.
4. Describe any new action name and whether it must be approval-gated.

Security-sensitive reports belong in the process described in
[SECURITY.md](SECURITY.md), not in a public issue.
