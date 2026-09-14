import unittest

from metaforge_core.policy import ActionPolicy


class ActionPolicyTests(unittest.TestCase):
    def test_ordinary_actions_are_allowed(self) -> None:
        decision = ActionPolicy().decide(["test.run"])
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.requires_approval)

    def test_guarded_action_requires_approval_until_recorded(self) -> None:
        policy = ActionPolicy()
        pending = policy.decide(["git.push", "test.run"])
        approved = policy.decide(["git.push", "test.run"], approved=True)
        self.assertTrue(pending.requires_approval)
        self.assertEqual(pending.guarded_actions, ("git.push",))
        self.assertTrue(approved.allowed)
