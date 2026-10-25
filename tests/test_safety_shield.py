"""
Unit tests for Safety Shield & Conservative Action Envelope
"""

import os
import sys
import unittest

# Ensure repo root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.repair.safety_shield import (
    ActionReversibilityAnalyzer,
    ActionSafetyClass,
    SafetyEnvelopeShield,
    SafetyShieldConfig,
    ShieldDecision,
)


class TestSafetyShield(unittest.TestCase):
    def test_blocksworld_reversibility(self):
        analyzer = ActionReversibilityAnalyzer("domains/blocksworld/domain.pddl")
        # In Blocksworld, pick-up is reversed by put-down, stack is reversed by unstack
        self.assertEqual(analyzer.get_safety_class("pick-up"), ActionSafetyClass.REVERSIBLE)
        self.assertEqual(analyzer.get_safety_class("put-down"), ActionSafetyClass.REVERSIBLE)
        self.assertEqual(analyzer.get_safety_class("stack"), ActionSafetyClass.REVERSIBLE)
        self.assertEqual(analyzer.get_safety_class("unstack"), ActionSafetyClass.REVERSIBLE)

    def test_barman_irreversibility(self):
        analyzer = ActionReversibilityAnalyzer("domains/barman/domain.pddl")
        # grasp and leave are reversible
        self.assertEqual(analyzer.get_safety_class("grasp"), ActionSafetyClass.REVERSIBLE)
        self.assertEqual(analyzer.get_safety_class("leave"), ActionSafetyClass.REVERSIBLE)
        # shake permanently destroys ingredients into cocktail; no reverse
        self.assertEqual(analyzer.get_safety_class("shake"), ActionSafetyClass.IRREVERSIBLE)

    def test_rovers_irreversibility(self):
        analyzer = ActionReversibilityAnalyzer("domains/rovers/domain.pddl")
        self.assertEqual(analyzer.get_safety_class("navigate"), ActionSafetyClass.REVERSIBLE)
        # sample_soil consumes soil sample permanently
        self.assertEqual(analyzer.get_safety_class("sample_soil"), ActionSafetyClass.IRREVERSIBLE)

    def test_hybrid_shield_interception(self):
        cfg = SafetyShieldConfig(enabled=True, mode="hybrid")
        shield = SafetyEnvelopeShield("domains/barman/domain.pddl", config=cfg)

        # 1. Grasp is reversible -> DISPATCH
        dec, msg = shield.evaluate_step(
            step_index=0,
            action_name="grasp",
            ground_args=["hand1", "shot1"],
            current_state={"(ontable shot1)", "(handempty hand1)"},
        )
        self.assertEqual(dec, ShieldDecision.DISPATCH)

        # 2. Shake is irreversible and uncertified -> INTERCEPT
        dec, msg = shield.evaluate_step(
            step_index=1,
            action_name="shake",
            ground_args=["cocktail1", "ingredient1", "ingredient2", "shaker1", "hand1", "hand2", "l1"],
            current_state={"(holding hand1 shaker1)", "(handempty hand2)"},
        )
        self.assertEqual(dec, ShieldDecision.INTERCEPT)
        self.assertEqual(len(shield.interception_history), 1)
        self.assertIn("virtual interception", shield.interception_history[0].reason)


if __name__ == "__main__":
    unittest.main()
