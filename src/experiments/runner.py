"""
runner.py
=========
Unified CLI Entrypoint for all Thesis Experiments.

Usage:
  python -m src.experiments.runner --config configs/experiments/repair_benchmark.yaml
  python -m src.experiments.runner --experiment repair
  python -m src.experiments.runner --experiment topology
  python -m src.experiments.runner --experiment ablation
  python -m src.experiments.runner --experiment baseline
  python -m src.experiments.runner --experiment audit
  python -m src.experiments.runner --all
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import yaml

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.experiments.ablation_study import run_ablation_suite
from src.experiments.baseline_comparison import run_baseline_comparison
from src.experiments.claim_audit import run_claim_audit
from src.experiments.measure_learning_burden import main as run_learning_burden_suite
from src.experiments.measure_planning_burden import run_planning_burden_suite
from src.experiments.partial_observability import run_partial_observability_benchmark
from src.experiments.repair_benchmark import run_repair_benchmark
from src.experiments.topology_collapse import run_topology_collapse_suite

EXPERIMENT_MAP = {
    "repair": (run_repair_benchmark, "configs/experiments/repair_benchmark.yaml"),
    "topology": (run_topology_collapse_suite, "configs/experiments/topology_collapse.yaml"),
    "ablation": (run_ablation_suite, "configs/experiments/ablation_study.yaml"),
    "baseline": (run_baseline_comparison, "configs/experiments/baseline_comparison.yaml"),
    "audit": (run_claim_audit, "configs/experiments/claim_audit.yaml"),
    "partial_obs": (run_partial_observability_benchmark, "configs/experiments/partial_observability.yaml"),
    "planning_burden": (run_planning_burden_suite, "configs/experiments/planning_burden.yaml"),
    "learning_burden": (run_learning_burden_suite, "configs/experiments/learning_burden.yaml"),
}


def run_from_config(config_path: str) -> Any:
    p = Path(config_path)
    if not p.exists():
        p = Path(__file__).resolve().parent.parent.parent / config_path
    if not p.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    raw_yaml = yaml.safe_load(p.read_text(encoding="utf-8"))
    exp_name = str(raw_yaml.get("experiment", raw_yaml.get("experiment_name", ""))).lower()

    if "partial" in exp_name:
        return run_partial_observability_benchmark(str(p))
    elif "learning_burden" in exp_name:
        return run_learning_burden_suite()
    elif "planning_burden" in exp_name:
        return run_planning_burden_suite()
    elif "repair" in exp_name:
        return run_repair_benchmark(str(p))
    elif "topology" in exp_name or "burden" in exp_name:
        return run_topology_collapse_suite(str(p))
    elif "ablation" in exp_name:
        return run_ablation_suite(str(p))
    elif "baseline" in exp_name or "learner" in exp_name:
        return run_baseline_comparison(str(p))
    elif "claim" in exp_name or "audit" in exp_name:
        return run_claim_audit(str(p))
    else:
        raise ValueError(
            f"Unrecognized experiment name '{exp_name}' in {config_path}. "
            f"Supported names contain: repair, topology, ablation, baseline, audit, partial, planning_burden, learning_burden."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Unified Experiment Runner for Thesis Benchmark Suite (YAML-driven)"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to YAML configuration file (e.g. configs/experiments/repair_benchmark.yaml)",
    )
    parser.add_argument(
        "--experiment",
        "-e",
        type=str,
        choices=list(EXPERIMENT_MAP.keys()),
        help="Experiment shortcut name (repair, topology, ablation, baseline, audit)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all experiment suites sequentially",
    )

    args = parser.parse_args()

    if args.all:
        print("\n=======================================================")
        print("RUNNING ALL EXPERIMENT SUITES")
        print("=======================================================\n")
        for name, (fn, default_cfg) in EXPERIMENT_MAP.items():
            print(f"\n>>> Running Experiment Suite: {name.upper()} ({default_cfg})")
            fn(default_cfg)
        return

    if args.config:
        run_from_config(args.config)
        return

    if args.experiment:
        fn, default_cfg = EXPERIMENT_MAP[args.experiment]
        fn(default_cfg)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
