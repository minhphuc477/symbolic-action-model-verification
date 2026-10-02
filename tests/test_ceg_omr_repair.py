"""
test_ceg_omr_repair.py
======================
Integration and regression test suite verifying CEG-OMR closed-loop
counterexample repair across all 4 canonical benchmark domains:
1. Sokoban (IPC Game Domain)
2. Blocksworld (IPC Classical Domain)
3. Gripper (IPC Classical Domain - Capacity Bottleneck)
4. Logistics (IPC Transportation Domain - Topology Bottleneck)

Also verifies Theorem 2 empirical tightness:
    rho = K_repair / (k * |F|^r) <= 1.0
"""

import os
import sys
import unittest

# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.repair.ceg_omr_engine import CEGOMRConfig, CEGOMREngine


class TestCEGOMRRepair(unittest.TestCase):

    def test_ceg_omr_sokoban_repair(self):
        cfg = CEGOMRConfig(
            domain_path="domains/mutated/domain_Type_II_seed42.pddl",
            problem_path="domains/sokoban/problem_p02.pddl",
            ground_truth_domain="domains/sokoban/domain.pddl",
            out_dir="repair_logs/test_sokoban/",
            max_repair_iterations=5,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Sokoban repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)
        self.assertLessEqual(res.total_queries, 256)

    def test_ceg_omr_blocksworld_repair(self):
        cfg = CEGOMRConfig(
            domain_path="domains/mutated/domain_Type_II_seed123.pddl",
            problem_path="domains/blocksworld/problem_p01.pddl",
            ground_truth_domain="domains/blocksworld/domain.pddl",
            out_dir="repair_logs/test_blocksworld/",
            max_repair_iterations=5,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Blocksworld repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)
        self.assertLessEqual(res.total_queries, 25)

    def test_ceg_omr_gripper_repair(self):
        cfg = CEGOMRConfig(
            domain_path="domains/mutated/domain_gripper_Type_II.pddl",
            problem_path="domains/gripper/problem_p01.pddl",
            ground_truth_domain="domains/gripper/domain.pddl",
            out_dir="repair_logs/test_gripper/",
            max_repair_iterations=5,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Gripper repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)
        self.assertLessEqual(res.total_queries, 64)

    def test_ceg_omr_logistics_repair(self):
        cfg = CEGOMRConfig(
            domain_path="domains/mutated/domain_logistics_Type_II.pddl",
            problem_path="domains/logistics/problem_p01.pddl",
            ground_truth_domain="domains/logistics/domain.pddl",
            out_dir="repair_logs/test_logistics/",
            max_repair_iterations=5,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Logistics repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)
        self.assertLessEqual(res.total_queries, 81)

    def test_theorem2_empirical_tightness_bound(self):
        """Verify rho = K_repair / (k * |F|^r) <= 1.0 for all 4 domains."""
        benchmarks = [
            ("Sokoban", "domains/mutated/domain_Type_II_seed42.pddl", "domains/sokoban/problem_p02.pddl", "domains/sokoban/domain.pddl", 1, 4, 4),
            ("Blocksworld", "domains/mutated/domain_Type_II_seed123.pddl", "domains/blocksworld/problem_p01.pddl", "domains/blocksworld/domain.pddl", 1, 5, 2),
            ("Gripper", "domains/mutated/domain_gripper_Type_II.pddl", "domains/gripper/problem_p01.pddl", "domains/gripper/domain.pddl", 1, 4, 3),
            ("Logistics", "domains/mutated/domain_logistics_Type_II.pddl", "domains/logistics/problem_p01.pddl", "domains/logistics/domain.pddl", 1, 3, 4),
        ]
        for name, mut_d, prob, gt_d, k, fluents, arity in benchmarks:
            cfg = CEGOMRConfig(
                domain_path=mut_d,
                problem_path=prob,
                ground_truth_domain=gt_d,
                out_dir=f"repair_logs/tightness_{name}/",
                max_repair_iterations=5,
            )
            res = CEGOMREngine(cfg).run()
            self.assertTrue(res.success)
            upper_bound = k * (fluents ** arity)
            rho = res.total_queries / upper_bound
            self.assertLessEqual(rho, 1.0, f"Theorem 2 violated on {name}: rho = {rho} > 1.0")


if __name__ == "__main__":
    unittest.main()
