"""
Paper 1 Visualization & Plot Generation Module
Generates publication-quality figures for AIJ submission:
1. Scatter Plot: A_pred vs R_play (Highlighting the Counterexample Region)
2. Phase Transition Plot: CPR vs PER
3. Multi-Model Comparative Bar Charts (LOCM2, FAMA, FastLAS, SLAF, ARMS)
"""

import os
import json
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

class BenchmarkPlotter:
    def __init__(self, output_dir="f:/Thesis/literature/figures"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_scatter_apred_vs_rplay(self, results_data, filename="scatter_apred_rplay.png"):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        sa_vals = [r.get("A_pred", r.get("SA", 0.95)) * 100 if r.get("A_pred", 0) <= 1.0 else r.get("A_pred", 95.0) for r in results_data]
        rplay_vals = [100.0 if r.get("R_play") == "INFINITY" or r.get("R_play") == "Infinity" else float(r.get("R_play", 0)) for r in results_data]
        
        ax.scatter(sa_vals, rplay_vals, alpha=0.6, color='crimson', edgecolors='k', s=30)
        ax.axvline(x=95.0, color='blue', linestyle='--', label='95% A_pred Threshold')
        ax.axhline(y=99.0, color='red', linestyle=':', label='R_play = Infinity Collapse')
        
        ax.set_xlabel('Passive Transition Accuracy (A_pred %)', fontsize=12)
        ax.set_ylabel('Execution Play Regret (R_play)', fontsize=12)
        ax.set_title('Paper 1: A_pred vs R_play Counterexample Region', fontsize=14)
        ax.legend()
        
        save_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_phase_transition_cpr_vs_per(self, results_data, filename="phase_transition_cpr_per.png"):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        cpr_vals = [r.get("CPR", 50.0) for r in results_data]
        per_vals = [r.get("PER", 10.0) for r in results_data]
        
        ax.scatter(cpr_vals, per_vals, alpha=0.6, color='darkgreen', s=30)
        ax.axvline(x=40.0, color='red', linestyle='--', label='CPR* = 40% Transition Boundary')
        
        ax.set_xlabel('Critical Precondition Recall (CPR %)', fontsize=12)
        ax.set_ylabel('Phantom Edge Rate (PER %)', fontsize=12)
        ax.set_title('Paper 1: Phase Transition of CPR vs PER', fontsize=14)
        ax.legend()
        
        save_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_model_comparison_bar_chart(self, summary_json_path="f:/Thesis/literature/paper1_empirical_benchmark_results.json", filename="bar_chart_metrics_comparison.png"):
        if not os.path.exists(summary_json_path):
            return None
            
        with open(summary_json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        models = list(summary.keys())
        apred_means = [summary[m]["A_pred_mean"] * 100 for m in models]
        apred_stds = [summary[m]["A_pred_std"] * 100 for m in models]
        collapse_rates = [summary[m]["topology_collapse_rate_pct"] for m in models]

        x = np.arange(len(models))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(10, 6))

        rects1 = ax1.bar(x - width/2, apred_means, width, yerr=apred_stds, label='Passive Accuracy A_pred (%)', color='royalblue', capsize=5)

        ax2 = ax1.twinx()
        rects2 = ax2.bar(x + width/2, collapse_rates, width, label='Search-Tree Collapse Rate (%)', color='firebrick')

        ax1.set_xlabel('Symbolic Action Model Learner', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Passive Accuracy A_pred (%)', fontsize=12, color='royalblue')
        ax2.set_ylabel('Search-Tree Collapse Rate (%)', fontsize=12, color='firebrick')
        ax1.set_xticks(x)
        ax1.set_xticklabels(models, fontsize=11, fontweight='bold')
        ax1.set_ylim(80, 100)
        ax2.set_ylim(0, 100)

        plt.title('Benchmark Model Comparison: Passive Accuracy vs Search-Tree Collapse', fontsize=14, fontweight='bold')
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        save_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def generate_all_plots(self, benchmark_results_json="f:/Thesis/literature/benchmark_results_50k.json"):
        results_data = []
        if os.path.exists(benchmark_results_json):
            with open(benchmark_results_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                results_data = data.get("all_results", [])
                
        p1 = self.plot_scatter_apred_vs_rplay(results_data)
        p2 = self.plot_phase_transition_cpr_vs_per(results_data)
        p3 = self.plot_model_comparison_bar_chart()
        return [p1, p2, p3]


if __name__ == "__main__":
    plotter = BenchmarkPlotter()
    generated = plotter.generate_all_plots()
    print("=== Benchmark Plotter Module Executed Cleanly ===")
    for g in generated:
        print(f"Generated Figure: {g}")
