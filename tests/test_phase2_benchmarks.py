"""
test_phase2_benchmarks.py
Unit and Integration tests for Phase 2 benchmarks:
- safe_ground variable substitution (verifying zero '??' bugs)
- fama_cleaner
- locm2_translator
- fastlas_translator
- transition_accuracy
- fair_comparator
"""

import os
import sys
import unittest

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.adapters.fama_cleaner import clean_fama_pddl
from src.adapters.fastlas_translator import translate_fastlas_rules_to_pddl
from src.adapters.locm2_translator import translate_locm2_pddl
from src.metrics.fair_comparator import compare_fairly
from src.metrics.transition_accuracy import evaluate_transition_accuracy, safe_ground


class TestSafeGround(unittest.TestCase):
    def test_strip_question_mark_no_double_qmark(self):
        # Case 1: param key has leading '?'
        pmap1 = {"?o1": "block_a", "?o2": "block_b"}
        lit1 = "(on ?o1 ?o2)"
        res1 = safe_ground(lit1, pmap1)
        self.assertEqual(res1, "(on block_a block_b)")
        self.assertNotIn("??", res1)

        # Case 2: param key does NOT have leading '?'
        pmap2 = {"o1": "block_a", "o2": "block_b"}
        res2 = safe_ground(lit1, pmap2)
        self.assertEqual(res2, "(on block_a block_b)")
        self.assertNotIn("??", res2)

    def test_word_boundary_safety(self):
        # Ensure ?o1 does not replace prefix of ?o10
        pmap = {"?o1": "block_a", "?o10": "block_z"}
        lit = "(and (clear ?o1) (ontable ?o10))"
        res = safe_ground(lit, pmap)
        self.assertEqual(res, "(and (clear block_a) (ontable block_z))")

class TestAdaptersAndTranslators(unittest.TestCase):
    def test_fama_cleaner_strips_zeros_and_types(self):
        raw = "(:action test :parameters (?x - object) :effect (and (clear ?x) 0))"
        cleaned = clean_fama_pddl(raw)
        self.assertNotIn(" 0)", cleaned)
        self.assertNotIn("- object", cleaned)

    def test_locm2_translation_validity(self):
        locm_raw = """
        (define (domain Blocksworld)
          (:action pick :parameters (?zero - zero ?b1 - b1)
           :precondition (and (zero_fsm0_state0) (b1_fsm0_state0))
           :effect (and (zero_fsm0_state1 ?v0 - b1) (b1_fsm0_state1 ?v0 - zero)))
        )
        """
        pddl_out = translate_locm2_pddl(locm_raw)
        self.assertIn("pick-up", pddl_out)
        self.assertNotIn("?zero", pddl_out)
        self.assertNotIn("?v0", pddl_out)

    def test_fastlas_translation(self):
        rules = "pick(V0) :- clear(V0), hand_empty, on_table(V0)."
        pddl_out = translate_fastlas_rules_to_pddl(rules)
        self.assertIn("pick-up", pddl_out)
        self.assertIn("(clear ?o1)", pddl_out)
        self.assertIn("(handempty)", pddl_out)

class TestEmpiricalMetrics(unittest.TestCase):
    def test_ground_truth_transition_accuracy(self):
        gt_path = "benchmark_outputs/ground_truth.pddl"
        if os.path.exists(gt_path):
            with open(gt_path, "r", encoding="utf-8") as f:
                gt_text = f.read()
            res = evaluate_transition_accuracy(gt_text)
            self.assertEqual(res["total_transitions"], 100)
            self.assertEqual(res["a_pred"], 1.0)
            self.assertEqual(res["a_appl"], 1.0)

    def test_fair_comparator_on_fama(self):
        gt_path = "benchmark_outputs/ground_truth.pddl"
        fama_path = "benchmark_outputs/fama_normalized.pddl"
        if os.path.exists(gt_path) and os.path.exists(fama_path):
            with open(gt_path, "r", encoding="utf-8") as f:
                gt_text = f.read()
            with open(fama_path, "r", encoding="utf-8") as f:
                fama_text = f.read()
            res = compare_fairly(gt_text, fama_text, fama_path, "Full Model (SAT-based)")
            self.assertTrue(res["pddl_valid"])
            self.assertEqual(res["d_triangle"], 2)
            self.assertEqual(res["a_pred"], 0.66)
            self.assertEqual(res["a_appl"], 1.0)

    def test_proposition1_phantom_divergence(self):
        from src.verification.proposition1_precondition_intervention import (
            run_precondition_intervention_suite,
        )
        res = run_precondition_intervention_suite()
        # Verify Control achieves PESR = 1.0, R_play = 0 on Task 1
        ctrl_t1 = res["Control (Ground Truth M*)"]["tasks"]["Task 1: Tower Inversion"]
        self.assertEqual(ctrl_t1["PESR"], 1.0)
        self.assertEqual(ctrl_t1["R_play"], "0")
        
        # Verify Omit (clear ?o1) in unstack achieves A_pred = 1.0 but collapses PESR = 0.0, R_play = INFINITY
        omit_clear = res["Omit (clear ?o1) in unstack"]
        self.assertEqual(omit_clear["A_pred"], 1.0)
        omit_t1 = omit_clear["tasks"]["Task 1: Tower Inversion"]
        self.assertEqual(omit_t1["PESR"], 0.0)
        self.assertEqual(omit_t1["R_play"], "INFINITY")
        self.assertEqual(omit_t1["phantom_edges"], 1)

if __name__ == "__main__":
    unittest.main()


