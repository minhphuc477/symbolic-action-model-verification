"""
ablation_study.py
=================
YAML-driven ablation study evaluating:
  1. Offline Backtracking (enable_backtracking)
  2. STRIPS Effect Coherence Ranking (use_effect_coherence)

Driven by:
  - configs/experiments/ablation_study.yaml
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Ensure repo root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.interventions.pddl_mutator import PDDLMutator
from src.repair.ceg_omr_engine import CEGOMRConfig, CEGOMREngine


def run_ablation_suite(
    config_file: str = "configs/experiments/ablation_study.yaml",
) -> list[dict[str, Any]]:
    cfg_p = Path(config_file)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_file
    exp_cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))

    out_file = Path(exp_cfg.get("output_file", "benchmark_outputs/ablation_study_results.json"))
    out_file.parent.mkdir(parents=True, exist_ok=True)
    mutated_dir = Path("domains/mutated/ablation")
    mutated_dir.mkdir(parents=True, exist_ok=True)

    benchmark_tasks = exp_cfg.get("tasks", [])
    ablation_modes = exp_cfg.get("ablations", [])

    mutator = PDDLMutator(seed=42)
    results: list[dict[str, Any]] = []

    print("=" * 80)
    print("RUNNING SYSTEMATIC ABLATION EXPERIMENTS")
    print(f"Config: {config_file}")
    print("=" * 80)

    for task in benchmark_tasks:
        dname = task["domain"]
        dgt = task["domain_gt"]
        prob = task["problem"]
        pname = Path(prob).stem
        faults_pool = [tuple(f) for f in task["target_faults"]]

        for k in [1, 2]:
            active_faults = faults_pool[:k]
            mut_path, _removed = mutator.apply_k_precondition_omissions(
                domain_path=dgt,
                k=k,
                target_actions_and_atoms=active_faults,
                out_dir=mutated_dir,
            )

            print(f"\n>>> Domain={dname} | Problem={pname} | k={k}")

            for mode in ablation_modes:
                mode_name = mode["name"]
                bt = mode["enable_backtracking"]
                coh = mode["use_effect_coherence"]

                config = CEGOMRConfig(
                    domain_path=mut_path,
                    problem_path=prob,
                    ground_truth_domain=dgt,
                    max_repair_iterations=20,
                    seed=42,
                    out_dir=f"repair_logs/ablation_{dname}_{pname}_k{k}_{mode_name.replace(' ', '_')}/",
                    enable_backtracking=bt,
                    use_effect_coherence=coh,
                )
                engine = CEGOMREngine(config)
                t0 = time.perf_counter()
                res = engine.repair()
                wall_time = time.perf_counter() - t0

                record = {
                    "domain": dname,
                    "problem": pname,
                    "k_faults": k,
                    "mode": mode_name,
                    "enable_backtracking": bt,
                    "use_effect_coherence": coh,
                    "success": res.success,
                    "total_queries": res.total_queries,
                    "iterations": res.iterations,
                    "wall_clock_seconds": round(wall_time, 3),
                    "error_message": res.error_message,
                }
                results.append(record)
                print(f"  [{mode_name:<25}] Success={res.success} | Queries={res.total_queries} | Iters={res.iterations} | Time={wall_time:.2f}s")

    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[Ablation Suite] Finished! Saved {len(results)} records to {out_file}")
    return results


if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "configs/experiments/ablation_study.yaml"
    run_ablation_suite(cfg_file)
