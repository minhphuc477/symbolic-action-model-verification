"""
Counterexample Verifier Module for Paper 1
Computes exact search-tree topology metrics, phantom path divergence (d_delta),
passive prediction accuracy (A_pred), and play regret (R_play) for standard theoretical counterexamples.
"""

from typing import Dict, Any, List, Tuple
from src.metrics.topology_metrics import TopologyMetricsCalculator

def run_counterexample_verification() -> Dict[str, Any]:
    """
    Evaluates Proposition 1 search-tree topology collapse metrics on 2 standardized counterexamples:
    1. Linear Chain (b=1, D=100)
    2. Binary Tree (b=2, D=3)
    """
    # ---------------------------------------------------------
    # Counterexample 1: Linear Chain (b=1, D=100)
    # Blocked at d=50 by p_50. Omitting p_50 unblocks 50 phantom edges (s50 -> s100).
    # ---------------------------------------------------------
    gt_edges_chain = [(f"s{i}", "move", f"s{i+1}") for i in range(50)]
    pred_edges_chain = [(f"s{i}", "move", f"s{i+1}", []) for i in range(100)]
    calc_chain = TopologyMetricsCalculator(gt_edges_chain, pred_edges_chain, ["p_50"])
    metrics_chain = calc_chain.compute_all_metrics(["p_50"])

    # ---------------------------------------------------------
    # Counterexample 2: Binary Tree (b=2, D=3)
    # Full tree has 15 nodes (s0..s14), 14 edges.
    # Blocked at d=1 (s0 -> s2) by p*.
    # Ground truth GT has left subtree only (7 edges).
    # Omitting p* unblocks right subtree (7 phantom edges).
    # ---------------------------------------------------------
    # Ground truth edges (left subtree only)
    gt_edges_tree = [
        ("s0", "act_left", "s1"),
        ("s1", "act_left", "s3"), ("s1", "act_right", "s4"),
        ("s3", "act_left", "s7"), ("s3", "act_right", "s8"),
        ("s4", "act_left", "s9"), ("s4", "act_right", "s10")
    ]
    # Learned edges (full tree, omitting p*)
    pred_edges_tree = [
        ("s0", "act_left", "s1", []),
        ("s0", "act_right", "s2", ["p*"]), # Phantom edge at d=1
        ("s1", "act_left", "s3", []), ("s1", "act_right", "s4", []),
        ("s2", "act_left", "s5", ["p*"]), ("s2", "act_right", "s6", ["p*"]),
        ("s3", "act_left", "s7", []), ("s3", "act_right", "s8", []),
        ("s4", "act_left", "s9", []), ("s4", "act_right", "s10", []),
        ("s5", "act_left", "s11", ["p*"]), ("s5", "act_right", "s12", ["p*"]),
        ("s6", "act_left", "s13", ["p*"]), ("s6", "act_right", "s14", ["p*"])
    ]
    calc_tree = TopologyMetricsCalculator(gt_edges_tree, pred_edges_tree, ["p*"])
    metrics_tree = calc_tree.compute_all_metrics(["p*"])

    return {
        "Linear_Chain_b1_D100": {
            "d_delta": metrics_chain["GED"],
            "A_pred": metrics_chain["Accuracy"],
            "Play_Regret_R_play": "INFINITY" if metrics_chain["Added_Phantom_Edges"] > 0 else 0,
            "metrics": metrics_chain
        },
        "Binary_Tree_b2_D3": {
            "d_delta": metrics_tree["GED"],
            "A_pred": metrics_tree["Accuracy"],
            "Play_Regret_R_play": "INFINITY" if metrics_tree["Added_Phantom_Edges"] > 0 else 0,
            "metrics": metrics_tree
        }
    }

if __name__ == "__main__":
    res = run_counterexample_verification()
    print("=== Proposition 1 Counterexample Verification Complete ===")
    print(res)
