"""
Unit Tests for Planning Burden (H_P) and Learning Burden (B)
Strictly adheres to RESEARCH_RULES.md: deterministic execution, no fake tests.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.metrics.learning_burden import compute_learning_burden, compute_play_regret
from src.metrics.planning_burden import compute_planning_burden
from src.metrics.transition_accuracy import ActionSchema, parse_pddl_model
from src.verification.proposition1_precondition_intervention import (
    PDDLForwardPlanner,
    get_benchmark_tasks,
)


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

    def test_24intervention_matrix_integrity(self):
        from src.experiments.measure_planning_burden import (
            get_full_24intervention_matrix,
        )
        matrix = get_full_24intervention_matrix()
        self.assertEqual(len(matrix), 8)
        total_interventions = 0
        for domain_name, dom_cfg in matrix.items():
            self.assertEqual(len(dom_cfg["interventions"]), 3)
            total_interventions += len(dom_cfg["interventions"])
            with open(dom_cfg["ref_file"], "r", encoding="utf-8") as f:
                schemas = parse_pddl_model(f.read())
            for int_spec in dom_cfg["interventions"]:
                act = int_spec["action"]
                omit = int_spec["omit_literal"].strip().lower()
                matching_act = [k for k in schemas if k.lower() == act.lower()]
                self.assertTrue(len(matching_act) > 0, f"Action {act} not in {domain_name}")
                sch = schemas[matching_act[0]]
                self.assertIn(omit, [p.strip().lower() for p in sch.preconditions])
        self.assertEqual(total_interventions, 24)

    def test_bidirectional_search_divergence_observed(self):
        import json
        out_file = "benchmark_outputs/planning_burden_results.json"
        self.assertTrue(os.path.exists(out_file), "Results file must exist")
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        summary = data["summary"]
        self.assertEqual(summary["total_interventions"], 24)
        # Verify Proposition 2: Both shortcuts (Delta H < 0) and detours (Delta H > 0) are empirically observed
        self.assertGreater(summary["phantom_shortcuts_count"], 0)
        self.assertGreater(summary["phantom_detours_count"], 0)
        self.assertGreaterEqual(summary["execution_failures_count"], 12)

    def test_scale_verification_exponential_divergence(self):
        import json
        out_file = "benchmark_outputs/scale_and_binding_results.json"
        self.assertTrue(os.path.exists(out_file), "Scale and binding results file must exist")
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        bw_data = data["scale_verification"]["blocksworld"]
        # Monotonically increasing Delta H_P for Blocksworld detours
        delta_hps = [r["delta_hp"] for r in bw_data]
        self.assertTrue(delta_hps[0] < delta_hps[1] < delta_hps[2], f"Delta H_P must grow with scale: {delta_hps}")
        # Monotonically decreasing Delta H_P for Hanoi shortcuts
        han_data = data["scale_verification"]["hanoi"]
        han_delta = [r["delta_hp"] for r in han_data]
        self.assertTrue(han_delta[0] > han_delta[1], f"Hanoi shortcut must intensify with scale: {han_delta}")

    def test_binding_preconditions_all_fail(self):
        import json
        out_file = "benchmark_outputs/scale_and_binding_results.json"
        self.assertTrue(os.path.exists(out_file), "Scale and binding results file must exist")
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        binding = data["binding_verification"]
        self.assertEqual(len(binding), 8)
        for int_id, rec in binding.items():
            self.assertEqual(rec["pesr"], 0.0, f"Intervention {int_id} must fail on binding task")
            self.assertEqual(rec["r_play"], "INFINITY")

if __name__ == "__main__":
    unittest.main()
