"""
Partial Observability Sensitivity Benchmark for CEG-OMR
======================================================
Tests the robustness of CEG-OMR when the Oracle Verifier provides
partially observed states at execution failure:
  p_obs in {1.0, 0.8, 0.6}
Under partial observability, unobserved fluents test the robustness of:
1. Version Space Candidate Elimination
2. Offline Backtracking & Refutation Memoization
Strictly adheres to RESEARCH_RULES.md: zero fake metrics, fully deterministic.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any

import yaml

from src.repair import (
    CEGOMRConfig,
    CEGOMREngine,
    Counterexample,
    OracleVerifier,
)


class PartiallyObservableVerifier(OracleVerifier):
    """
    Oracle Verifier subclass simulating partial observability by randomly masking
    state fluents at execution failure with probability (1 - obs_prob).
    """

    def __init__(
        self,
        ground_truth_domain: str,
        problem_path: str,
        obs_prob: float = 1.0,
        seed: int = 42,
    ):
        super().__init__(ground_truth_domain, problem_path)
        self.obs_prob = obs_prob
        self._rng = random.Random(seed)

    def verify_prefix(
        self, plan: list[str], learned_domain: str
    ) -> tuple[bool, Counterexample | None, int]:
        success, cx, queries = super().verify_prefix(plan, learned_domain)
        if cx and self.obs_prob < 1.0 and cx.current_state:
            # Mask out fluents with probability (1 - obs_prob)
            literals = re.findall(r"\([^()]+\)", cx.current_state)
            retained = [lit for lit in literals if self._rng.random() < self.obs_prob]
            cx.current_state = "{" + ", ".join(retained) + "}"
        return success, cx, queries


def run_partial_observability_benchmark(
    config_path: str = "configs/experiments/partial_observability.yaml",
) -> dict[str, Any]:
    """Runs the partial observability sensitivity suite based on YAML configuration."""
    cfg_p = Path(config_path)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_path

    raw_cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    domains = raw_cfg["domains"]
    obs_levels = raw_cfg.get("observability_levels", [1.0, 0.8, 0.6])
    seed = raw_cfg.get("seed", 42)
    max_iters = raw_cfg.get("max_repair_iterations", 30)
    enable_backtrack = raw_cfg.get("enable_backtracking", True)
    use_coherence = raw_cfg.get("use_effect_coherence", True)
    out_file = Path(raw_cfg.get("output_path", "benchmark_outputs/partial_observability_results.json"))

    results: dict[str, Any] = {}

    for d in domains:
        d_name = d["name"]
        dom_path = d["domain_path"]
        prob_path = d["problem_path"]
        search_str = d["search_str"]
        repl_str = d["replace_str"]

        results[d_name] = {}
        # Prepare mutated domain
        text = Path(dom_path).read_text(encoding="utf-8")
        mut_dir = Path(f"domains/mutated/pobs_{d_name}")
        mut_dir.mkdir(parents=True, exist_ok=True)
        mut_path = mut_dir / "domain.pddl"
        mut_path.write_text(text.replace(search_str, repl_str), encoding="utf-8")

        for p_obs in obs_levels:
            print(f"Testing {d_name} at p_obs={p_obs}...")
            config = CEGOMRConfig(
                domain_path=str(mut_path),
                problem_path=prob_path,
                ground_truth_domain=dom_path,
                max_repair_iterations=max_iters,
                seed=seed,
                out_dir=f"repair_logs/pobs_{d_name}_{int(p_obs * 100)}/",
                enable_backtracking=enable_backtrack,
                use_effect_coherence=use_coherence,
            )
            engine = CEGOMREngine(config)
            engine.verifier = PartiallyObservableVerifier(
                ground_truth_domain=dom_path,
                problem_path=prob_path,
                obs_prob=p_obs,
                seed=seed,
            )
            res = engine.run()
            results[d_name][str(p_obs)] = {
                "success": res.success,
                "queries": res.total_queries,
                "iterations": res.iterations,
                "error": res.error_message,
            }
            print(f"--> {d_name} (p_obs={p_obs}): Success={res.success}, Queries={res.total_queries}")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved partial observability results to: {out_file}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="CEG-OMR Partial Observability Benchmark")
    parser.add_argument("--config", default="configs/experiments/partial_observability.yaml", help="Path to YAML config")
    args = parser.parse_args()
    run_partial_observability_benchmark(args.config)


if __name__ == "__main__":
    main()
