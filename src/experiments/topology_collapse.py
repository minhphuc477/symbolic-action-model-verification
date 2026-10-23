"""
topology_collapse.py
====================
YAML-driven verification of Search-Tree Topology Collapse & Planning Burden.
Measures:
  1. Planning Burden H_P(M*, x) vs H_P(M_hat, x) across 24 interventions
  2. Phenomenological divergence: Phantom Shortcuts (Delta H_P < 0) vs Phantom Detours (Delta H_P > 0)
  3. Scale Verification: Exponential divergence on Blocksworld and Hanoi scaling instances
  4. Binding Precondition Verification: Multi-capacity non-colocated tasks

Driven by:
  - configs/experiments/topology_collapse.yaml
  - configs/interventions/matrix_24.yaml
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.experiments.measure_planning_burden import (
    run_planning_burden_suite,
)
from src.experiments.scale_and_binding_verification import (
    run_binding_precondition_suite as run_binding_verification,
)
from src.experiments.scale_and_binding_verification import (
    run_scale_verification,
)


def run_topology_collapse_suite(
    config_file: str = "configs/experiments/topology_collapse.yaml",
) -> dict[str, Any]:
    cfg_p = Path(config_file)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_file
    exp_cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))

    print("=" * 80)
    print("RUNNING SEARCH-TREE TOPOLOGY COLLAPSE & PLANNING BURDEN SUITE")
    print(f"Config: {config_file}")
    print("=" * 80)

    # 1. Planning Burden across 24 interventions
    t0 = time.perf_counter()
    burden_res = run_planning_burden_suite()

    # 2. Scale Verification
    scale_res = run_scale_verification()

    # 3. Binding Verification
    binding_res = run_binding_verification()

    elapsed = time.perf_counter() - t0
    combined = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config": exp_cfg,
        "runtime_seconds": round(elapsed, 3),
        "planning_burden": burden_res,
        "scale_verification": scale_res,
        "binding_verification": binding_res,
    }
    print(f"\n[Topology Collapse Suite] Completed in {elapsed:.2f}s")
    return combined


if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "configs/experiments/topology_collapse.yaml"
    run_topology_collapse_suite(cfg_file)
