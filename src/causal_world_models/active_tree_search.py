"""
Active Search-Tree Rollout & Verification Engine
================================================
Integrated with the Unified Flagship CEG-OMR Architecture:
Replaces dead mock stubs with direct delegation to CEGOMREngine.
"""

from __future__ import annotations

from typing import Any

from src.repair.ceg_omr_engine import CEGOMRConfig, CEGOMREngine


class ActiveTreeSearchRollout:
    """
    Executes goal-directed model repair rollouts to eliminate phantom paths
    under rule interventions.
    """

    def __init__(self, max_iterations: int = 50, seed: int = 42):
        self.max_iterations = max_iterations
        self.seed = seed

    def execute_active_verification_rollout(
        self,
        domain_path: str,
        problem_path: str,
        gt_domain_path: str = "",
        out_dir: str = "repair_logs/",
    ) -> dict[str, Any]:
        """
        Executes active model repair loop using native Fast Downward and Oracle verifier.
        """
        config = CEGOMRConfig(
            domain_path=domain_path,
            problem_path=problem_path,
            ground_truth_domain=gt_domain_path,
            max_repair_iterations=self.max_iterations,
            seed=self.seed,
            out_dir=out_dir,
        )
        engine = CEGOMREngine(config)
        result = engine.run()

        return {
            "success": result.success,
            "total_queries": result.total_queries,
            "iterations": result.iterations,
            "play_regret_after": result.play_regret_after,
            "wall_clock_seconds": result.wall_clock_seconds,
            "repaired_domain_path": result.repaired_domain_path,
            "num_counterexamples": len(result.counterexamples),
            "status": "ACTIVE_REPAIR_SUCCESS" if result.success else "ACTIVE_REPAIR_FAILED",
        }
