"""
Compute Real Empirical Benchmark Summary Statistics from Executed Runs
Calculates mean and std of A_pred, d_delta, PESR, and failure rate across models.
"""

import json
import os
from collections import defaultdict
import numpy as np

def compute_summary(json_path: str = "f:/Thesis/literature/benchmark_results_50k.json", out_path: str = "f:/Thesis/literature/paper1_empirical_benchmark_results.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("all_results", data.get("sample_results", []))
    model_stats = defaultdict(lambda: {"A_pred": [], "d_delta": [], "PESR": [], "R_play_inf_count": 0, "total": 0})

    for r in results:
        m = r.get("model")
        if not m or r.get("status") != "SUCCESS":
            continue
        model_stats[m]["A_pred"].append(r.get("A_pred", 0.0))
        model_stats[m]["d_delta"].append(r.get("d_delta", 0))
        model_stats[m]["PESR"].append(r.get("PESR", 0.0))
        if r.get("R_play") == "INFINITY":
            model_stats[m]["R_play_inf_count"] += 1
        model_stats[m]["total"] += 1

    summary = {}
    for m, vals in model_stats.items():
        summary[m] = {
            "evaluated_runs": vals["total"],
            "A_pred_mean": float(np.mean(vals["A_pred"])),
            "A_pred_std": float(np.std(vals["A_pred"])),
            "d_delta_mean": float(np.mean(vals["d_delta"])),
            "d_delta_std": float(np.std(vals["d_delta"])),
            "PESR_mean": float(np.mean(vals["PESR"])),
            "PESR_std": float(np.std(vals["PESR"])),
            "topology_collapse_rate_pct": float(vals["R_play_inf_count"] / vals["total"] * 100) if vals["total"] > 0 else 0.0
        }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("=== Real Benchmark Summary Computation Complete ===")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    compute_summary()
