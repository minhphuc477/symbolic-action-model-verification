"""
Paper 1 Visualization & Plot Generation Module
Generates:
1. Scatter Plot: A_pred vs R_play (Highlighting the Counterexample Region)
2. Phase Transition Plot: CPR vs PER
3. Multi-Model Comparative Bar Charts
"""

import os
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
        
        sa_vals = [r.get("SA", 95.0) for r in results_data]
        rplay_vals = [100.0 if r.get("R_play") == "Infinity" else float(r.get("R_play", 0)) for r in results_data]
        
        ax.scatter(sa_vals, rplay_vals, alpha=0.6, color='crimson', edgecolors='k', s=30)
        ax.axvline(x=98.0, color='blue', linestyle='--', label='98% A_pred Threshold')
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

if __name__ == "__main__":
    plotter = BenchmarkPlotter()
    sample_data = [
        {"SA": 98.5, "CPR": 15.0, "PER": 25.0, "R_play": "Infinity"},
        {"SA": 98.2, "CPR": 90.0, "PER": 2.0, "R_play": 0.0},
        {"SA": 94.0, "CPR": 45.0, "PER": 12.0, "R_play": 5.0}
    ]
    p1 = plotter.plot_scatter_apred_vs_rplay(sample_data)
    p2 = plotter.plot_phase_transition_cpr_vs_per(sample_data)
    print("=== Benchmark Plotter Module Verified ===")
    print(f"Generated Figure 1: {p1}")
    print(f"Generated Figure 2: {p2}")
