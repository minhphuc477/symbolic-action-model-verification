"""
generate_figures.py
===================
Publication-Quality Figure Generator for Thesis.
Generates:
  1. figures/fig1_method_comparison.{pdf,png}
  2. figures/fig2_multifault_scaling.{pdf,png}
  3. figures/fig3_empirical_tightness_rho.{pdf,png}
  4. figures/fig4_ablation_backtracking.{pdf,png}
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Matplotlib Publication Style Settings
plt.rcParams.update({
    "font.size": 10,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
    "mathtext.fontset": "stix",
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

FIG_DIR = Path("figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Colorblind-safe palette (Wong 2011)
CB_BLUE = "#0072B2"
CB_ORANGE = "#E69F00"
CB_GREEN = "#009E73"
CB_RED = "#D55E00"
CB_PURPLE = "#CC79A7"
CB_GREY = "#7F7F7F"


def make_fig1():
    fair_bench = json.loads(Path("benchmark_outputs/fair_comparison_benchmark.json").read_text(encoding="utf-8"))

    methods_ordered = [
        ("CEG-OMR (Proposed Active)", "CEG-OMR\n(Proposed)", CB_BLUE),
        ("Active SAM (Juba & Stern 2021 §4)", "Active SAM\n(Closed-Loop)", CB_ORANGE),
        ("Passive SAM / Random AML (M=50)", "Passive SAM\n(M=50)", CB_GREEN),
        ("Passive SAM / Random AML (M=250)", "Passive SAM\n(M=250)", CB_PURPLE),
        ("Naive Replanning (Fox et al. ICAPS 2006)", "Naive Replan\n(Control)", CB_GREY),
    ]

    labels = [m[1] for m in methods_ordered]
    colors = [m[2] for m in methods_ordered]

    pesr = []
    queries = []
    for full_name, _, _ in methods_ordered:
        recs = [d for d in fair_bench if d["method"] == full_name]
        pesr.append(np.mean([r["pesr_after"] for r in recs]) * 100)
        queries.append(np.mean([r["k_env_queries"] for r in recs]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.0))

    # Panel (a): Plan Execution Success Rate
    bars1 = ax1.bar(labels, pesr, color=colors, width=0.55, edgecolor="black", linewidth=0.7)
    ax1.set_ylabel("PESR After Repair (%)")
    ax1.set_title("(a) Plan Execution Success Rate (PESR)", loc="left", fontsize=10, weight="bold")
    ax1.set_ylim(0, 120)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 2.5, f"{yval:.0f}%", ha="center", va="bottom", fontsize=8)

    # Panel (b): Active Queries K_repair (Log scale due to M=250 vs K=8)
    bars2 = ax2.bar(labels, queries, color=colors, width=0.55, edgecolor="black", linewidth=0.7)
    ax2.set_ylabel("Environment Queries ($K_{\\mathrm{env}}$)")
    ax2.set_title("(b) Query Cost ($K_{\\mathrm{env}}$, Log Scale)", loc="left", fontsize=10, weight="bold")
    ax2.set_yscale("log")
    ax2.set_ylim(1, 400)
    ax2.yaxis.set_major_formatter(ticker.ScalarFormatter())

    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval * 1.15, f"{yval:.1f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig1_method_comparison.pdf")
    fig.savefig(FIG_DIR / "fig1_method_comparison.png")
    plt.close()
    print("Generated Fig 1: Fair Method Comparison")


def make_fig2():
    stats_rep = json.loads(Path("benchmark_outputs/statistical_analysis_report.json").read_text(encoding="utf-8"))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.7))

    ks = [1, 2, 3]
    q_means = [stats_rep["multi_fault_scaling_by_k"][f"k_{k}"]["queries_mean"] for k in ks]
    q_stds = [stats_rep["multi_fault_scaling_by_k"][f"k_{k}"]["queries_std"] for k in ks]
    it_means = [stats_rep["multi_fault_scaling_by_k"][f"k_{k}"]["iters_mean"] for k in ks]

    # Panel (a): Queries vs k
    ax1.plot(ks, q_means, marker="o", color=CB_BLUE, linewidth=1.8, markersize=6, label="Empirical $K_{\\mathrm{repair}}$")
    ax1.fill_between(ks, np.array(q_means) - np.array(q_stds), np.array(q_means) + np.array(q_stds), color=CB_BLUE, alpha=0.15)
    ax1.set_xlabel("Number of Injected Faults ($k$)")
    ax1.set_ylabel("Mean Queries ($K_{\\mathrm{repair}}$)")
    ax1.set_title("(a) Query Scaling vs. Fault Multiplicity ($k$)", loc="left", fontsize=10, weight="bold")
    ax1.set_xticks(ks)
    ax1.set_ylim(0, 20)
    ax1.legend(loc="upper left")

    # Panel (b): Repair Iterations vs k
    ax2.plot(ks, it_means, marker="s", color=CB_GREEN, linewidth=1.8, markersize=6, label="Repair Iterations")
    ax2.set_xlabel("Number of Injected Faults ($k$)")
    ax2.set_ylabel("Mean Repair Iterations")
    ax2.set_title("(b) Solver Rounds vs. Fault Multiplicity ($k$)", loc="left", fontsize=10, weight="bold")
    ax2.set_xticks(ks)
    ax2.set_ylim(0, 5)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig2_multifault_scaling.pdf")
    fig.savefig(FIG_DIR / "fig2_multifault_scaling.png")
    plt.close()
    print("Generated Fig 2: Multi-Fault Scaling")


def make_fig3():
    main_bench = json.loads(Path("benchmark_outputs/comprehensive_multi_fault_benchmark.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(5.5, 3.0))

    domains = ["Sokoban", "Logistics", "Gripper", "Blocksworld"]
    ceg_recs = [d for d in main_bench if d["method"] == "CEG-OMR (Proposed)"]

    data_by_dom = []
    for d in domains:
        vals = [r["empirical_tightness_rho"] for r in ceg_recs if r["domain"] == d]
        data_by_dom.append(vals)

    ax.boxplot(
        data_by_dom,
        tick_labels=domains,
        patch_artist=True,
        widths=0.45,
        medianprops={"color": "black", "linewidth": 1.5},
        boxprops={"facecolor": "#D9E8F5", "edgecolor": CB_BLUE, "linewidth": 1.2},
        whiskerprops={"color": CB_BLUE, "linewidth": 1.2},
        capprops={"color": CB_BLUE, "linewidth": 1.2},
    )

    # Plot individual data points with jitter
    rng = np.random.default_rng(42)
    for i, vals in enumerate(data_by_dom):
        x = rng.normal(i + 1, 0.04, size=len(vals))
        ax.scatter(x, vals, color=CB_BLUE, alpha=0.7, s=28, zorder=3)

    # Theoretical upper bound line
    ax.axhline(1.0, color=CB_RED, linestyle="--", linewidth=1.5, label="Theorem 2 Bound ($\\rho = 1.0$)")

    ax.set_ylabel("Empirical Tightness Ratio $\\rho = \\frac{K_{\\mathrm{repair}}}{k \\cdot |F|^r}$")
    ax.set_title("Empirical Tightness Ratio $\\rho \\ll 1.0$ Across Domains", loc="left", fontsize=10, weight="bold")
    ax.set_ylim(-0.05, 1.15)
    ax.legend(loc="upper right")

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig3_empirical_tightness_rho.pdf")
    fig.savefig(FIG_DIR / "fig3_empirical_tightness_rho.png")
    plt.close()
    print("Generated Fig 3: Empirical Tightness Ratio")


def make_fig4():
    stats_rep = json.loads(Path("benchmark_outputs/statistical_analysis_report.json").read_text(encoding="utf-8"))
    ablation_bench = json.loads(Path("benchmark_outputs/ablation_study_results.json").read_text(encoding="utf-8"))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.8))

    modes = ["Full\nCEG-OMR", "No\nBacktracking", "No-Heuristic\n(Uniform)"]
    mode_keys = ["Full CEG-OMR", "No-Backtracking", "No-Heuristic (Uniform)"]

    all_succ = [stats_rep["ablation_summary"][k]["success_rate"] * 100 for k in mode_keys]

    # Logistics specific success rate
    log_recs = [d for d in ablation_bench if d["domain"] == "Logistics"]
    log_succ = []
    for k in mode_keys:
        m_recs = [r for r in log_recs if r["mode"] == k]
        log_succ.append(sum(1.0 for r in m_recs if r["success"]) / len(m_recs) * 100)

    x = np.arange(len(modes))
    width = 0.35

    # Panel (a): Overall vs Logistics Success Rate
    ax1.bar(x - width / 2, all_succ, width, label="All 4 Domains", color=CB_BLUE, edgecolor="black", linewidth=0.7)
    bars_log = ax1.bar(x + width / 2, log_succ, width, label="Logistics Only", color=CB_ORANGE, edgecolor="black", linewidth=0.7)

    ax1.set_ylabel("Repair Success Rate (%)")
    ax1.set_title("(a) Repair Success Under Ablations", loc="left", fontsize=10, weight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes)
    ax1.set_ylim(0, 125)
    ax1.legend(loc="upper right", framealpha=0.8)

    for bar in bars_log:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 2.5, f"{yval:.0f}%", ha="center", va="bottom", fontsize=8)

    # Panel (b): Mean Iterations across ablations
    iters = [stats_rep["ablation_summary"][k]["iters_mean"] for k in mode_keys]
    bars_it = ax2.bar(modes, iters, width=0.45, color=[CB_BLUE, CB_RED, CB_GREEN], edgecolor="black", linewidth=0.7)
    ax2.set_ylabel("Mean Repair Iterations")
    ax2.set_title("(b) Solver Iterations to Convergence", loc="left", fontsize=10, weight="bold")
    ax2.set_ylim(0, 4)
    for bar in bars_it:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, f"{yval:.2f}", ha="center", va="bottom", fontsize=8.5)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig4_ablation_backtracking.pdf")
    fig.savefig(FIG_DIR / "fig4_ablation_backtracking.png")
    plt.close()
    print("Generated Fig 4: Ablation Comparison")


def generate_all_figures():
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print(f"\nAll publication figures successfully written to {FIG_DIR.resolve()}")


if __name__ == "__main__":
    generate_all_figures()
