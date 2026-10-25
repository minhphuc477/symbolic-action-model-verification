"""
CEG-OMR Main Closed-Loop Repair Engine
======================================
Coordinates Generator (Fast Downward), Verifier (Oracle / Environment execution),
and Synthesizer (Active Horn Version Space Elimination with Minimal Relaxation Abduction)
under Algorithm 1.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

from src.repair.config import CEGOMRConfig, CEGOMRResult
from src.repair.generator import FastDownwardGenerator
from src.repair.horn_synthesizer import HornSynthesizer
from src.repair.verifier import OracleVerifier


class CEGOMREngine:
    """
    Main CEG-OMR repair loop.

    Algorithm 1:
    ──────────────────────────────────────────────────────
    Input : M_hat_0 (learned model), M* (oracle), s_0, S_g
    Output: Repaired M_hat_K with R_play(M_hat_K) = 0

      K <- 0; M_hat <- M_hat_0
      WHILE K < max_iterations:
        pi* <- Generator(M_hat, s_0, S_g)          # Fast Downward
        IF pi* = NULL:
          TRY Backtrack(M_hat) OR MinimalRelaxationAbduction(M_hat)
          IF still NULL: RETURN (UNSOLVABLE, K)
        (success, xi) <- Verifier(pi*, M*)        # Oracle execution
        IF success: RETURN (M_hat, K)             # R_play = 0
        M_hat <- Synthesizer(M_hat, xi)           # Bidirectional Horn-clause repair
        K <- K + |xi.step_index|
      RETURN (FAILED, K)
    ──────────────────────────────────────────────────────
    """

    def __init__(self, config: CEGOMRConfig):
        self.config = config
        self.generator = FastDownwardGenerator(config)
        self.verifier = OracleVerifier(
            config.ground_truth_domain or config.domain_path,
            config.problem_path,
        )
        self.synthesizer = HornSynthesizer(
            out_dir=config.out_dir,
            seed=config.seed,
            use_effect_coherence=config.use_effect_coherence,
            allow_effect_deletion=config.allow_effect_deletion,
            max_relaxation_size=config.max_relaxation_size,
            max_suspects_per_level=config.max_suspects_per_level,
        )
        self._rng = random.Random(config.seed)

    def repair(self) -> CEGOMRResult:
        """Alias for run() to provide clean semantic interface."""
        return self.run()

    def run(self) -> CEGOMRResult:
        """Execute the full CEG-OMR repair loop and return a CEGOMRResult."""
        out_dir = Path(self.config.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        result = CEGOMRResult(success=False, total_queries=0, iterations=0)
        current_domain = self.config.domain_path
        self.synthesizer._ensure_initial_preconditions(current_domain)
        t_start = time.perf_counter()

        print(f"[CEG-OMR] Starting repair: {Path(current_domain).name}")
        print(f"[CEG-OMR] Max iterations: {self.config.max_repair_iterations}")

        for iteration in range(self.config.max_repair_iterations):
            result.iterations = iteration + 1
            plan_file = str(out_dir / f"plan_iter{iteration:03d}.soln")

            # ── GENERATOR ───────────────────────────────────────────────
            print(f"[CEG-OMR] Iter {iteration}: running Fast Downward...")
            plan_found, plan, elapsed = self.generator.generate_plan(
                current_domain, self.config.problem_path, plan_file
            )

            if not plan_found:
                if self.config.enable_backtracking:
                    # 1. Check for structural self-contradictions (score 20) or SAS+ sink-violation delete effects (score 18)
                    if self.config.allow_relaxation and bool(self.synthesizer.repair_history):
                        relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                            self.synthesizer.relax_overconstrained_domain(
                                current_domain,
                                self.config.problem_path,
                                self.generator,
                                iteration,
                                min_suspect_score=18,
                            )
                        )
                        if relaxed_ok and relaxed_plan:
                            current_domain = relaxed_path
                            plan_found = True
                            plan = relaxed_plan
                            elapsed = relaxed_elapsed
                            print(
                                f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction resolved structural "
                                f"over-constraint -> {Path(relaxed_path).name} ({len(plan)} steps)"
                            )

                    # 2. If the last added candidate was a low-confidence guess (score < 10), backtrack first
                    last_score = (
                        self.synthesizer.repair_history[-1].get("chosen_score", 0)
                        if self.synthesizer.repair_history else 0
                    )
                    if not plan_found and last_score >= 10 and self.config.allow_relaxation:
                        relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                            self.synthesizer.relax_overconstrained_domain(
                                current_domain,
                                self.config.problem_path,
                                self.generator,
                                iteration,
                                min_suspect_score=12,
                            )
                        )
                        if relaxed_ok and relaxed_plan:
                            current_domain = relaxed_path
                            plan_found = True
                            plan = relaxed_plan
                            elapsed = relaxed_elapsed
                            print(
                                f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction resolved compound "
                                f"over-constraint -> {Path(relaxed_path).name} ({len(plan)} steps)"
                            )

                    if not plan_found:
                        rolled_back, rolled_path = self.synthesizer.rollback(iteration)
                        if rolled_back and rolled_path:
                            print(f"[CEG-OMR] Planner unsolvable. Backtracking to alternative hypothesis -> {Path(rolled_path).name}")
                            current_domain = rolled_path
                            continue

                        if self.config.allow_relaxation:
                            relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                                self.synthesizer.relax_overconstrained_domain(
                                    current_domain,
                                    self.config.problem_path,
                                    self.generator,
                                    iteration,
                                    min_suspect_score=0,
                                )
                            )
                            if relaxed_ok and relaxed_plan:
                                current_domain = relaxed_path
                                plan_found = True
                                plan = relaxed_plan
                                elapsed = relaxed_elapsed
                                print(
                                    f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction restored solvability "
                                    f"-> {Path(relaxed_path).name} ({len(plan)} steps)"
                                )
                            else:
                                result.error_message = (
                                    f"Generator returned no plan at iteration {iteration} and no backtrack/relaxation hypothesis remaining"
                                )
                                print("[CEG-OMR] No plan found and no backtrack/relaxation candidate remaining. Stopping.")
                                break
                        else:
                            result.error_message = f"Generator returned no plan at iteration {iteration} and relaxation is disabled"
                            print("[CEG-OMR] No plan found and relaxation is disabled. Stopping.")
                            break
                else:
                    result.error_message = f"Generator returned no plan at iteration {iteration} and backtracking is disabled"
                    print("[CEG-OMR] No plan found and no backtrack candidate remaining. Stopping.")
                    break

            print(f"[CEG-OMR] Iter {iteration}: plan found ({len(plan)} steps, {elapsed:.2f}s)")

            # ── ORACLE VERIFIER ──────────────────────────────────────────
            goal_reached, counterexample, queries = self.verifier.verify_prefix(
                plan, current_domain
            )
            result.total_queries += queries
            result.per_iteration_queries.append(queries)

            if goal_reached:
                result.success = True
                result.play_regret_after = 0.0
                result.repaired_domain_path = current_domain
                print(f"[CEG-OMR] SUCCESS at iteration {iteration}. K_repair = {result.total_queries}")
                break

            if counterexample is None:
                result.error_message = "Verifier returned no counterexample despite failure"
                break

            result.counterexamples.append(counterexample)
            print(f"[CEG-OMR] Iter {iteration}: counterexample found -- {counterexample}")

            # ── SYNTHESIZER ──────────────────────────────────────────────
            repaired_path = self.synthesizer.repair(current_domain, counterexample, iteration)
            current_domain = repaired_path
            print(f"[CEG-OMR] Iter {iteration}: domain repaired -> {Path(repaired_path).name}")

        result.wall_clock_seconds = time.perf_counter() - t_start
        result.repaired_domain_path = current_domain

        # Persist result as JSON log
        log_path = out_dir / "ceg_omr_result.json"
        log_path.write_text(
            json.dumps({
                "success": result.success,
                "total_queries": result.total_queries,
                "iterations": result.iterations,
                "wall_clock_seconds": round(result.wall_clock_seconds, 3),
                "play_regret_before": result.play_regret_before,
                "play_regret_after": result.play_regret_after,
                "repaired_domain_path": result.repaired_domain_path,
                "counterexamples": [
                    {"step": cx.step_index, "action": cx.action, "type": cx.failure_type}
                    for cx in result.counterexamples
                ],
                "per_iteration_queries": result.per_iteration_queries,
                "error": result.error_message,
            }, indent=2),
            encoding="utf-8",
        )
        print(f"[CEG-OMR] Result log: {log_path}")
        return result
