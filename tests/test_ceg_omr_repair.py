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

    def test_ceg_omr_pitch_black_hazard_repair(self):
        """Verify hazard avoidance precondition repair on pitch_black game domain."""
        from pathlib import Path
        text = Path("domains/pitch_black/domain.pddl").read_text(encoding="utf-8")
        mut_dir = Path("domains/mutated/test_pb")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(text.replace("(is-light-on ?to)", ""), encoding="utf-8")

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/pitch_black/problem_p02.pddl",
            ground_truth_domain="domains/pitch_black/domain.pddl",
            out_dir="repair_logs/test_pb/",
            max_repair_iterations=10,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Pitch Black repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_dungeon_escape_key_gating_repair(self):
        """Verify inventory gating precondition repair with backtracking on dungeon_escape."""
        from pathlib import Path
        text = Path("domains/dungeon_escape/domain.pddl").read_text(encoding="utf-8")
        mut_dir = Path("domains/mutated/test_de")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(
            text.replace("(has-key ?p ?k)\n      (door-locked ?door)", "(door-locked ?door)"),
            encoding="utf-8",
        )

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/dungeon_escape/problem_p01.pddl",
            ground_truth_domain="domains/dungeon_escape/domain.pddl",
            out_dir="repair_logs/test_de/",
            max_repair_iterations=15,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Dungeon Escape repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_effect_delta_repair(self):
        """Verify Type III unpredicted delete effect induction (key consumption)."""
        from pathlib import Path
        gt_dir = Path("domains/mutated/test_eff_gt")
        gt_dir.mkdir(parents=True, exist_ok=True)
        gt_dom = gt_dir / "domain.pddl"

        orig_text = Path("domains/dungeon_escape/domain.pddl").read_text(encoding="utf-8")
        gt_text = orig_text.replace(
            ":effect (and\n      (door-open ?door)\n      (not (door-locked ?door))\n    )",
            ":effect (and\n      (door-open ?door)\n      (not (door-locked ?door))\n      (not (has-key ?p ?k))\n    )"
        )
        gt_dom.write_text(gt_text, encoding="utf-8")

        mut_dir = Path("domains/mutated/test_eff_mut")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(orig_text, encoding="utf-8")

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/dungeon_escape/problem_p01.pddl",
            ground_truth_domain=str(gt_dom),
            out_dir="repair_logs/test_eff_log/",
            max_repair_iterations=10,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Effect delta repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_same_action_multi_fault_repair(self):
        """Verify k=2 missing preconditions on the SAME action (pick-up missing both clear and handempty)."""
        from pathlib import Path

        from src.interventions.pddl_mutator import PDDLMutator
        mut_dir = Path("domains/mutated/test_same_act_k2")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom, removed = PDDLMutator(seed=42).apply_k_precondition_omissions(
            domain_path="domains/blocksworld/domain.pddl",
            k=2,
            target_actions_and_atoms=[("pick-up", "(clear ?x)"), ("pick-up", "(handempty)")],
            out_dir=mut_dir,
        )
        self.assertEqual(len(removed), 2)

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/blocksworld/problem_p01.pddl",
            ground_truth_domain="domains/blocksworld/domain.pddl",
            out_dir="repair_logs/test_same_act_k2/",
            max_repair_iterations=15,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Same-action k=2 repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_spurious_precondition_abduction(self):
        """Verify Minimal-Relaxation Abduction when M_hat_0 has a spurious precondition making it unsolvable."""
        from pathlib import Path
        orig_text = Path("domains/blocksworld/domain.pddl").read_text(encoding="utf-8")
        # Inject spurious precondition (holding ?x) into pick-up (classic LLM/over-constrained error)
        mut_text = orig_text.replace(
            ":precondition (and (clear ?x) (ontable ?x) (handempty))",
            ":precondition (and (clear ?x) (ontable ?x) (handempty) (holding ?x))",
        )
        mut_dir = Path("domains/mutated/test_spurious_prec")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(mut_text, encoding="utf-8")

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/blocksworld/problem_p01.pddl",
            ground_truth_domain="domains/blocksworld/domain.pddl",
            out_dir="repair_logs/test_spurious_prec/",
            max_repair_iterations=10,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Spurious precondition abduction failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_bidirectional_spurious_effect_repair(self):
        """Verify 4-Way Effect Delta Induction removes spurious add and spurious delete effects."""
        from pathlib import Path
        orig_text = Path("domains/blocksworld/domain.pddl").read_text(encoding="utf-8")
        # Inject spurious add effect (ontable ?x) and spurious delete effect (not (clear ?y)) into pick-up / unstack
        mut_text = orig_text.replace(
            ":effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))",
            ":effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x) (clear ?x))",
        )
        mut_dir = Path("domains/mutated/test_spurious_eff")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(mut_text, encoding="utf-8")

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/blocksworld/problem_p01.pddl",
            ground_truth_domain="domains/blocksworld/domain.pddl",
            out_dir="repair_logs/test_spurious_eff/",
            max_repair_iterations=10,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Bidirectional spurious effect repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)

    def test_ceg_omr_compound_bidirectional_fault_repair(self):
        """
        Verify compound fault repair combining:
          1. Missing precondition (clear ?x) on unstack (Delta Pre^-)
          2. Spurious precondition (holding ?x) on pick-up (Delta Pre^+)
          3. Missing delete effect (not (clear ?y)) on stack (Delta Eff^-)
        """
        from pathlib import Path
        orig_text = Path("domains/blocksworld/domain.pddl").read_text(encoding="utf-8")
        mut_text = (
            orig_text.replace(
                ":precondition (and (on ?x ?y) (clear ?x) (handempty))",
                ":precondition (and (on ?x ?y) (handempty))",
            )
            .replace(
                ":precondition (and (clear ?x) (ontable ?x) (handempty))",
                ":precondition (and (clear ?x) (ontable ?x) (handempty) (holding ?x))",
            )
            .replace(
                ":effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y))",
                ":effect (and (not (holding ?x)) (clear ?x) (handempty) (on ?x ?y))",
            )
        )
        mut_dir = Path("domains/mutated/test_compound_3way")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_dom = mut_dir / "domain.pddl"
        mut_dom.write_text(mut_text, encoding="utf-8")

        cfg = CEGOMRConfig(
            domain_path=str(mut_dom),
            problem_path="domains/blocksworld/problem_p01.pddl",
            ground_truth_domain="domains/blocksworld/domain.pddl",
            out_dir="repair_logs/test_compound_3way/",
            max_repair_iterations=15,
        )
        res = CEGOMREngine(cfg).run()
        self.assertTrue(res.success, f"Compound 3-way bidirectional repair failed: {res.error_message}")
        self.assertEqual(res.play_regret_after, 0.0)


if __name__ == "__main__":
    unittest.main()

