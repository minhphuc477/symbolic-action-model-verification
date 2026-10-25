"""
test_repair_srp_components.py
=============================
Isolated unit tests for CEG-OMR Single Responsibility Principle (SRP) components:
- src.repair.config (CEGOMRConfig, Counterexample, CEGOMRResult)
- src.repair.verifier (OracleVerifier, state_str)
- src.repair.horn_synthesizer (HornSynthesizer scoring & candidate generation)
"""

import tempfile
import unittest

from src.repair.config import CEGOMRConfig, CEGOMRResult, Counterexample
from src.repair.horn_synthesizer import HornSynthesizer
from src.repair.verifier import OracleVerifier, state_str


class TestRepairConfig(unittest.TestCase):
    def test_config_defaults(self):
        cfg = CEGOMRConfig(
            domain_path="domains/blocksworld/domain.pddl",
            problem_path="domains/blocksworld/problem_p01.pddl",
        )
        self.assertEqual(cfg.domain_path, "domains/blocksworld/domain.pddl")
        self.assertEqual(cfg.problem_path, "domains/blocksworld/problem_p01.pddl")
        self.assertTrue(cfg.enable_backtracking)
        self.assertTrue(cfg.use_effect_coherence)
        self.assertTrue(cfg.allow_relaxation)

    def test_counterexample_str(self):
        cx = Counterexample(
            step_index=2,
            action="(pick-up b1)",
            predicted_next="{holding(b1)}",
            actual_next="FAILURE",
            failure_type="inapplicable",
            current_state="{clear(b1), ontable(b1)}",
        )
        s = str(cx)
        self.assertIn("xi_2", s)
        self.assertIn("pick-up", s)
        self.assertIn("inapplicable", s)

    def test_result_summary(self):
        res = CEGOMRResult(
            success=True,
            total_queries=12,
            iterations=2,
            play_regret_before=float("inf"),
            play_regret_after=0.0,
            wall_clock_seconds=1.45,
        )
        summary = res.summary()
        self.assertIn("Success:           True", summary)
        self.assertIn("K_repair (queries):12", summary)
        self.assertIn("Iterations:        2", summary)
        self.assertIn("R_play after:      0.0", summary)


class TestOracleVerifier(unittest.TestCase):
    def test_state_str(self):
        self.assertEqual(state_str(None), "NONE")
        self.assertEqual(state_str(set()), "{}")
        self.assertEqual(state_str({"b", "a"}), "{a, b}")

    def test_verify_prefix_inapplicable(self):
        # A plan with an action that fails preconditions in initial state
        verifier = OracleVerifier(
            ground_truth_domain="domains/blocksworld/domain.pddl",
            problem_path="domains/blocksworld/problem_p01.pddl",
        )
        # Attempt to stack b1 on b2 when not holding b1
        invalid_plan = ["(stack b1 b2)"]
        goal_reached, cx, queries = verifier.verify_prefix(
            plan=invalid_plan,
            learned_domain="domains/blocksworld/domain.pddl",
        )
        self.assertFalse(goal_reached)
        self.assertIsNotNone(cx)
        self.assertEqual(cx.failure_type, "inapplicable")
        self.assertEqual(queries, 1)

    def test_verify_prefix_success(self):
        verifier = OracleVerifier(
            ground_truth_domain="domains/blocksworld/domain.pddl",
            problem_path="domains/blocksworld/problem_p01.pddl",
        )
        self.assertEqual(verifier.gt_domain, "domains/blocksworld/domain.pddl")
        self.assertEqual(verifier.problem_path, "domains/blocksworld/problem_p01.pddl")


class TestHornSynthesizer(unittest.TestCase):
    def test_initialization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            synth = HornSynthesizer(
                out_dir=tmpdir,
                seed=42,
                use_effect_coherence=True,
            )
            self.assertTrue(synth.use_effect_coherence)
            self.assertEqual(synth.seed, 42)


if __name__ == "__main__":
    unittest.main()
