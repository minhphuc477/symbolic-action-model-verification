"""
main.py
=======
Unified Master Entrypoint for the Thesis Codebase:
"From Search-Tree Topology Collapse to Counterexample-Guided Online Model Repair (CEG-OMR)"

Usage:
  1. Run status dashboard & smoke verification:
       python main.py
  2. Run any experiment suite via unified runner:
       python main.py --experiment repair
       python main.py --experiment topology
       python main.py --experiment ablation
       python main.py --experiment baseline
       python main.py --experiment partial_obs
       python main.py --experiment audit
       python main.py --config configs/experiments/repair_benchmark.yaml
"""

from __future__ import annotations

import sys

from src.adapters import PuzzleScriptAdapter
from src.experiments.claim_audit import run_claim_audit
from src.experiments.runner import main as runner_main
from src.metrics import TopologyMetricsCalculator
from src.verification import run_counterexample_verification


def run_dashboard_and_smoke_check() -> None:
    print("=" * 80)
    print("  UNIFIED THESIS FRAMEWORK: TOPOLOGY COLLAPSE DIAGNOSTIC & CEG-OMR REPAIR")
    print("=" * 80)

    # 1. Counterexample & Topology Collapse Smoke Verification
    print("\n[1/4] Verifying Theoretical Counterexample & Topology Collapse Engine...")
    counterexample_res = run_counterexample_verification()
    chain_res = counterexample_res["Linear_Chain_b1_D100"]
    tree_res = counterexample_res["Binary_Tree_b2_D3"]
    print(
        f"  -> Linear Chain (b=1, D=100): d_delta={chain_res['d_delta']}, "
        f"A_pred={chain_res['A_pred']*100:.1f}%, R_play={chain_res['Play_Regret_R_play']}"
    )
    print(
        f"  -> Binary Tree  (b=2, D=3)  : d_delta={tree_res['d_delta']}, "
        f"A_pred={tree_res['A_pred']*100:.1f}%, R_play={tree_res['Play_Regret_R_play']}"
    )

    # 2. Adapter & Metrics Smoke Check
    print("\n[2/4] Verifying Symbolic Adapter & Topology Metrics Calculator...")
    adapter = PuzzleScriptAdapter("Sokoban_Bench")
    fluents = adapter.parse_grid_state_to_fluents([[".", "P", "."], [".", "B", "."], [".", ".", "."]])
    real_edges = [("s0", "act_move", "s1"), ("s1", "act_door", "s2")]
    pred_edges = [
        ("s0", "act_move", "s1", []),
        ("s1", "act_door", "s2", ["p_key"]),
        ("s1", "act_shortcut", "s3", ["p_key"]),
    ]
    calculator = TopologyMetricsCalculator(real_edges, pred_edges, ["p_key"])
    metrics_res = calculator.compute_all_metrics(["p_normal"])
    print(
        f"  -> Adapter Fluents={len(fluents)} | GED={metrics_res['GED']} | "
        f"PER={metrics_res['PER_Phantom_Edge_Rate']}"
    )

    # 3. Result-to-Claim Audit Summary (All 5 Core Thesis Claims)
    print("\n[3/4] Running Automated Result-to-Claim Verification Audit (5 Core Claims)...")
    audit_report = run_claim_audit("configs/experiments/claim_audit.yaml")
    n_verified = sum(1 for r in audit_report["precheck_results"] if r["claim_supported"] == "yes")
    n_total = len(audit_report["precheck_results"])
    print(f"  -> Verified Claims: {n_verified}/{n_total} ({'100% PASS' if audit_report['all_verified'] else 'FAIL'})")

    # 4. Quick CLI Reference
    print("\n[4/4] Unified Experiment Runner Commands:")
    print("  python main.py --experiment topology      # Claim 1: 1,080-run Topology Collapse Audit")
    print("  python main.py --experiment baseline      # Claim 1B: FAMA / LOCM2 / FastLAS Baselines")
    print("  python main.py --experiment repair        # Claim 2: 72-run Bidirectional & Compound CEG-OMR")
    print("  python main.py --experiment ablation      # Claim 3: Effect Coherence & Backtracking Ablation")
    print("  python main.py --experiment partial_obs   # Claim 5: Partial Observability & Noise Robustness")
    print("  python main.py --experiment audit         # Full Result-to-Claim Verification Audit")
    print("=" * 80)


def main() -> None:
    if len(sys.argv) > 1:
        runner_main()
    else:
        run_dashboard_and_smoke_check()


if __name__ == "__main__":
    main()
