"""A deliberately narrow, explicit action-approval policy."""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_GUARDED_ACTIONS = frozenset(
    {"credential.use", "deploy", "git.push", "network.egress", "shell.destructive"}
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    guarded_actions: tuple[str, ...]


class ActionPolicy:
    """Classify requested action labels; enforcement stays with the host."""

    def __init__(self, guarded_actions: frozenset[str] = DEFAULT_GUARDED_ACTIONS) -> None:
        self._guarded_actions = guarded_actions

    def decide(self, actions: list[str], approved: bool = False) -> PolicyDecision:
        guarded = tuple(sorted(set(actions).intersection(self._guarded_actions)))
        return PolicyDecision(
            allowed=not guarded or approved,
            requires_approval=bool(guarded) and not approved,
            guarded_actions=guarded,
        )
