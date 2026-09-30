"""
Comprehensive Unit Test Suite for Thesis Benchmark & Verification Harness
Tests:
- PuzzleScriptAdapter
- TopologyMetricsCalculator
- CounterexampleVerifier
- RealAStarPlanner
- StatisticalRigorEngine
"""

import unittest
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapters import PuzzleScriptAdapter
from src.metrics import TopologyMetricsCalculator
from src.verification import run_counterexample_verification, RealAStarPlanner, PuzzleScriptGridState
from src.stats import StatisticalRigorEngine


class TestPuzzleScriptAdapter(unittest.TestCase):
    def test_fluent_parsing(self):
        adapter = PuzzleScriptAdapter("Sokoban")
        grid = [['.', 'P', '.'], ['.', 'B', '.'], ['.', '.', '.']]
        fluents = adapter.parse_grid_state_to_fluents(grid)
        self.assertIn('(at player pos_1_0)', fluents)
        self.assertIn('(at box pos_1_1)', fluents)

    def test_pddl_header_generation(self):
        adapter = PuzzleScriptAdapter("It Is Pitch Black")
        header = adapter.generate_pddl_domain_header()
        self.assertIn("(domain Pitch_Black)", header)


class TestTopologyMetricsCalculator(unittest.TestCase):
    def test_metric_computation(self):
        real_edges = [("s0", "act_move", "s1"), ("s1", "act_door", "s2")]
        pred_edges = [("s0", "act_move", "s1", []), ("s1", "act_door", "s2", ["p_key"]), ("s1", "act_shortcut", "s3", ["p_key"])]
        calculator = TopologyMetricsCalculator(real_edges, pred_edges, ["p_key"])
        metrics = calculator.compute_all_metrics(["p_normal"])
        
        self.assertEqual(metrics["PER_Phantom_Edge_Rate"], "33.33%")
        self.assertAlmostEqual(calculator.calculate_per(), 0.3333, places=2)


class TestCounterexampleVerifier(unittest.TestCase):
    def test_proposition1_counterexamples(self):
        res = run_counterexample_verification()
        self.assertIn('Linear_Chain_b1_D100', res)
        self.assertIn('Binary_Tree_b2_D3', res)
        
        chain = res['Linear_Chain_b1_D100']
        self.assertEqual(chain['d_delta'], 50)
        self.assertEqual(chain['Play_Regret_R_play'], 'INFINITY')


class TestRealAStarPlanner(unittest.TestCase):
    def test_astar_search_solve(self):
        planner = RealAStarPlanner()
        start_state, walls = planner.create_level("Door_Lock_Bottleneck")
        res = planner.solve_astar(start_state, paradigm="LOCM2", is_bottleneck=True)
        self.assertIn("A_pred", res)
        self.assertIn("d_delta", res)
        self.assertIn("PESR", res)
        self.assertIn("R_play", res)


class TestStatisticalRigorEngine(unittest.TestCase):
    def test_cohens_d(self):
        group1 = [10, 12, 14, 16, 18]
        group2 = [2, 4, 6, 8, 10]
        d = StatisticalRigorEngine.calculate_cohens_d(group1, group2)
        self.assertGreater(d, 0.8)  # Large effect size

    def test_bootstrap_ci(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        low, high = StatisticalRigorEngine.bootstrap_ci(data, num_bootstraps=100)
        self.assertLessEqual(low, high)


if __name__ == "__main__":
    unittest.main()
