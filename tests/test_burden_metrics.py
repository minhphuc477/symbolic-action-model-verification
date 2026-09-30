"""
Unit Tests for Planning Burden (H_P) and Learning Burden (B)
Strictly adheres to RESEARCH_RULES.md: deterministic execution, no fake tests.
"""

import unittest
import math
import os
from src.metrics.transition_accuracy import parse_pddl_model, ActionSchema
from src.verification.proposition1_precondition_intervention import (
    PDDLForwardPlanner,
    get_benchmark_tasks
)
from src.metrics.planning_burden import compute_planning_burden
from src.metrics.learning_burden import compute_play_regret, compute_learning_burden

class DummyLearner:
    def __init__(self, model_dict):
        self.model_dict = model_dict

    def learn(self, traces):
        return self.model_dict

class TestBurdenMetrics(unittest.TestCase):

    def setUp(self):
        gt_file = "benchmark_outputs/ground_truth.pddl"
        with open(gt_file, "r", encoding="utf-8") as f:
            gt_pddl = f.read()
        self.gt_models = parse_pddl_model(gt_pddl)
        self.tasks = get_benchmark_tasks()
        self.t1 = self.tasks["Task 1: Tower Inversion"]

    def test_planning_burden_control(self):
        hp, plan, nodes = compute_planning_burden(
            self.gt_models,
            self.t1["init"],
            self.t1["goal"],
            PDDLForwardPlanner,
            self.t1["objects"]
        )
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan), 6) # Optimal 6 steps
        self.assertGreater(nodes, 0)
        expected_hp = math.log2(1.0 + float(nodes))
        self.assertAlmostEqual(hp, expected_hp, places=4)

    def test_play_regret_control_zero(self):
        regret = compute_play_regret(
            self.gt_models,
            self.gt_models,
            self.t1,
            PDDLForwardPlanner
        )
        self.assertEqual(regret, 0.0)

    def test_play_regret_phantom_infinite(self):
        # Create an intervened model that omits 'clear' in unstack
        intervened = dict(self.gt_models)
        unstack = self.gt_models["unstack"]
        new_pre = [p for p in unstack.preconditions if not p.startswith("(clear")]
        raw_effects = unstack.add_effects + [f"(not {d})" for d in unstack.del_effects]
        intervened["unstack"] = ActionSchema(
            "unstack", unstack.params, new_pre, raw_effects
        )

        regret = compute_play_regret(
            intervened,
            self.gt_models,
            self.t1,
            PDDLForwardPlanner
        )
        self.assertEqual(regret, float('inf'))

    def test_learning_burden_mock_convergence(self):
        # Perfect learner converges at first budget
        learner = DummyLearner(self.gt_models)
        res = compute_learning_burden(
            learner=learner,
            domain=self.gt_models,
            problem=self.t1,
            trace_generator=lambda n, seed: [n],
            planner_class=PDDLForwardPlanner,
            epsilon=0.1,
            n_values=[10, 20, 50],
            n_seeds=2
        )
        self.assertTrue(res["converged"])
        self.assertEqual(res["B"], 10)

    def test_learning_burden_mock_infinite(self):
        # Broken learner never converges
        intervened = dict(self.gt_models)
        unstack = self.gt_models["unstack"]
        new_pre = [p for p in unstack.preconditions if not p.startswith("(clear")]
        raw_effects = unstack.add_effects + [f"(not {d})" for d in unstack.del_effects]
        intervened["unstack"] = ActionSchema(
            "unstack", unstack.params, new_pre, raw_effects
        )
        learner = DummyLearner(intervened)
        res = compute_learning_burden(
            learner=learner,
            domain=self.gt_models,
            problem=self.t1,
            trace_generator=lambda n, seed: [n],
            planner_class=PDDLForwardPlanner,
            epsilon=0.1,
            n_values=[10, 20],
            n_seeds=2
        )
        self.assertFalse(res["converged"])
        self.assertEqual(res["B"], float('inf'))

if __name__ == "__main__":
    unittest.main()
