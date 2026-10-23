"""
test_ceg_omr_multifault.py
===========================
Regression and unit test suite for:
1. Multi-fault mutation generation (k >= 2)
2. Multi-fault closed-loop counterexample repair (k = 2)
3. Hypothesis backtracking and domain AST rollback mechanism
4. Negated precondition candidate synthesis and ranking
5. Safe Action Model (SAM) baseline exploration and analysis
"""

import os
import sys
import unittest
from pathlib import Path

import pddl

# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interventions.pddl_mutator import PDDLMutator
from src.repair.ceg_omr_engine import (
    CEGOMRConfig,
    CEGOMREngine,
    Counterexample,
    HornSynthesizer,
)
from src.repair.sam_baseline import SAMBaseline


class TestCEGOMRMultiFaultAndFeatures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Path("domains/mutated").mkdir(parents=True, exist_ok=True)
        Path("repair_logs").mkdir(parents=True, exist_ok=True)

    def test_k_fault_mutation_generator(self):
        """Verify apply_k_precondition_omissions correctly removes k preconditions."""
        mutator = PDDLMutator(seed=42)
        domain_gt = "domains/blocksworld/domain.pddl"

        target_faults = [
            ("pick-up", "(handempty)"),
            ("stack", "(clear ?y)"),
        ]
        mut_path, removed = mutator.apply_k_precondition_omissions(
            domain_path=domain_gt,
            k=2,
            target_actions_and_atoms=target_faults,
            out_dir="domains/mutated",
        )
        self.assertEqual(len(removed), 2)

        # Parse mutated domain AST and verify omissions
        parsed_dom = pddl.parse_domain(mut_path)
        act_map = {a.name.lower(): a for a in parsed_dom.actions}

        # Check pick-up has no (handempty)
        pickup_pre = str(act_map["pick-up"].precondition).lower()
        self.assertNotIn("handempty", pickup_pre)

        # Check stack has no (clear ?y)
        stack_pre = str(act_map["stack"].precondition).lower()
        self.assertNotIn("clear", stack_pre)

    def test_multi_fault_repair_blocksworld_k2(self):
        """Verify CEG-OMR repairs k=2 simultaneous precondition omissions."""
        mutator = PDDLMutator(seed=42)
        domain_gt = "domains/blocksworld/domain.pddl"
        problem = "domains/blocksworld/problem_p01.pddl"
        target_faults = [
            ("pick-up", "(handempty)"),
            ("stack", "(clear ?y)"),
        ]
        mut_path, _ = mutator.apply_k_precondition_omissions(
            domain_path=domain_gt,
            k=2,
            target_actions_and_atoms=target_faults,
            out_dir="domains/mutated",
        )

        cfg = CEGOMRConfig(
            domain_path=mut_path,
            problem_path=problem,
            ground_truth_domain=domain_gt,
            out_dir="repair_logs/test_bw_k2/",
            max_repair_iterations=15,
            seed=42,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"k=2 repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)
        self.assertGreaterEqual(res.iterations, 1)
        self.assertLessEqual(res.total_queries, 25 * 2)

    def test_hypothesis_rollback_and_backtracking(self):
        """Verify that HornSynthesizer can rollback invalid candidate hypotheses."""
        mutator = PDDLMutator(seed=42)
        domain_gt = "domains/blocksworld/domain.pddl"
        mut_path, _ = mutator.apply_k_precondition_omissions(
            domain_path=domain_gt,
            k=1,
            target_actions_and_atoms=[("pick-up", "(handempty)")],
            out_dir="domains/mutated",
        )

        synthesizer = HornSynthesizer(out_dir="domains/mutated", seed=42)

        # Create a counterexample for pick-up
        ce = Counterexample(
            step_index=0,
            action="(pick-up a)",
            predicted_next="(holding a)",
            actual_next="FAILURE: precondition violation",
            failure_type="inapplicable",
            current_state="(clear a) (ontable a) (holding b)",  # hand is NOT empty!
        )

        # First repair synthesizes a candidate
        repaired_path = synthesizer.repair(mut_path, ce, iteration=0)
        self.assertTrue(Path(repaired_path).exists())
        self.assertEqual(len(synthesizer.repair_history), 1)
        chosen = synthesizer.repair_history[0]["chosen"]

        # Now simulate a backtracking call (e.g. planner returned unsolvable)
        backtrack_success, next_domain_path = synthesizer.rollback(iteration=1)
        self.assertTrue(backtrack_success)
        self.assertTrue(Path(next_domain_path).exists())
        self.assertEqual(len(synthesizer.repair_history), 0)
        # The chosen candidate should now be registered as refuted
        self.assertIn(chosen, synthesizer.refuted_candidates["pick-up"])

    def test_negated_precondition_ranking(self):
        """Verify negated candidate generation and ranking logic."""
        mutator = PDDLMutator(seed=42)
        domain_gt = "domains/blocksworld/domain.pddl"
        mut_path, _ = mutator.apply_k_precondition_omissions(
            domain_path=domain_gt,
            k=1,
            target_actions_and_atoms=[("pick-up", "(handempty)")],
            out_dir="domains/mutated",
        )

        synthesizer = HornSynthesizer(out_dir="domains/mutated", seed=42)

        # In a state where agent is holding block b, pick-up of block a fails:
        # Hand is not empty, and agent is holding b.
        ce = Counterexample(
            step_index=0,
            action="(pick-up a)",
            predicted_next="(holding a)",
            actual_next="FAILURE: precondition violation",
            failure_type="inapplicable",
            current_state="(clear a) (ontable a) (holding b)",
        )

        repaired_path = synthesizer.repair(mut_path, ce, iteration=0)
        self.assertTrue(Path(repaired_path).exists())
        parsed = pddl.parse_domain(repaired_path)
        pickup_act = next(a for a in parsed.actions if a.name.lower() == "pick-up")
        pickup_pre_str = str(pickup_act.precondition).lower()
        self.assertTrue(
            "handempty" in pickup_pre_str or "not" in pickup_pre_str,
            f"Expected handempty or negated holding in precondition, got: {pickup_pre_str}",
        )

    def test_sam_baseline_execution(self):
        """Verify SAM baseline collects exploratory traces and outputs result."""
        sam = SAMBaseline(seed=42)
        domain_gt = "domains/blocksworld/domain.pddl"
        problem = "domains/blocksworld/problem_p01.pddl"

        mutator = PDDLMutator(seed=42)
        mut_path, _ = mutator.apply_k_precondition_omissions(
            domain_path=domain_gt,
            k=1,
            target_actions_and_atoms=[("pick-up", "(handempty)")],
            out_dir="domains/mutated",
        )

        results = sam.run_exploration(
            domain_path=mut_path,
            problem_path=problem,
            gt_domain_path=domain_gt,
            sample_budgets=[10, 20],
            target_action="pick-up",
            missing_atom="(handempty)",
            out_dir="domains/mutated",
        )

        self.assertIn(10, results)
        self.assertIn(20, results)
        r20 = results[20]
        self.assertEqual(r20.total_samples, 20)
        self.assertIsInstance(r20.wall_clock_seconds, float)


if __name__ == "__main__":
    unittest.main()
