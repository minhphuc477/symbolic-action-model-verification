"""
run_phase2_benchmarks.py
End-to-End benchmark runner for Phase 2:
1. Runs FAMA, LOCM2, and FastLAS on Blocksworld in WSL.
2. Applies robust adapters/translators:
   - fama_cleaner.py: strips Madagascar SAT artifacts and type keywords.
   - locm2_translator.py: maps FSM transitions to standard STRIPS PDDL with sound add/del effects.
   - fastlas_translator.py: maps synthesized ASP/ILP rules into STRIPS PDDL.
3. Validates all 3 PDDL models with official 'pddl' package parser.
4. Evaluates all 3 normalized models against Ground Truth:
   - Precondition Precision, Recall, F1
   - Effect Precision, Recall, F1
   - Overall Action Model Symmetric Difference d_triangle (Graph Edit Distance)
   - Genuine State Transition Prediction Accuracy (A_pred) over 100 real transitions
   - Precondition Applicability Accuracy (A_appl)
5. Distinguishes Full-Model learners (FAMA, LOCM2) from Precondition-only learners (FastLAS).
"""

import os
import sys
import subprocess
import json

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.adapters.fama_cleaner import clean_fama_pddl
from src.adapters.locm2_translator import translate_locm2_file
from src.adapters.fastlas_translator import translate_fastlas_rules_to_pddl
from src.metrics.model_comparator import compare_action_models
from src.metrics.fair_comparator import compare_fairly
from src.metrics.transition_accuracy import evaluate_transition_accuracy

def run_phase2():
    os.makedirs("benchmark_outputs", exist_ok=True)
    
    # 1. Ground Truth
    gt_path = "daineto-meta-planning/src/meta_planning/dataset/blocks/reference"
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_pddl = f.read()
    with open("benchmark_outputs/ground_truth.pddl", "w", encoding="utf-8") as f:
        f.write(gt_pddl)

    print("=== Step 1: Running & Cleaning FAMA ===")
    fama_cmd = 'wsl bash -c "/mnt/f/Thesis/venv_linux/bin/python /mnt/f/Thesis/run_fama_test.py"'
    res_fama = subprocess.run(fama_cmd, shell=True, capture_output=True, text=True)
    fama_stdout = res_fama.stdout
    if "LEARNED PDDL DOMAIN MODEL:" in fama_stdout:
        fama_raw_pddl = fama_stdout.split("LEARNED PDDL DOMAIN MODEL:")[1].strip()
    else:
        fama_raw_pddl = fama_stdout.strip()
    fama_clean = clean_fama_pddl(fama_raw_pddl)
    fama_out_path = "benchmark_outputs/fama_normalized.pddl"
    with open(fama_out_path, "w", encoding="utf-8") as f:
        f.write(fama_clean)
    print("FAMA Normalized PDDL saved.")

    print("\n=== Step 2: Running & Translating LOCM2 ===")
    locm_cmd = 'wsl bash -c "cd /mnt/f/Thesis/locm_repo && /mnt/f/Thesis/venv_linux/bin/python locm2.py"'
    subprocess.run(locm_cmd, shell=True, capture_output=True, text=True)
    locm_raw_path = "locm_repo/output/Blocksworld/Blocksworld.pddl"
    locm_out_path = "benchmark_outputs/locm2_normalized.pddl"
    locm_clean = translate_locm2_file(locm_raw_path, locm_out_path)
    print("LOCM2 Normalized PDDL saved.")

    print("\n=== Step 3: Running & Translating FastLAS ===")
    fastlas_cmd = 'wsl bash -c "FastLAS /mnt/f/Thesis/test_fastlas.las"'
    res_fastlas = subprocess.run(fastlas_cmd, shell=True, capture_output=True, text=True)
    fastlas_rules = res_fastlas.stdout.strip()
    fastlas_clean = translate_fastlas_rules_to_pddl(fastlas_rules)
    fastlas_out_path = "benchmark_outputs/fastlas_normalized.pddl"
    with open(fastlas_out_path, "w", encoding="utf-8") as f:
        f.write(fastlas_clean)
    print("FastLAS Normalized PDDL saved.")

    print("\n=== Step 4: Comparing with Ground Truth & Evaluating Real Transition Accuracy ===")
    eval_fama = compare_fairly(gt_pddl, fama_clean, fama_out_path, learner_type="Full Model (SAT-based)")
    eval_locm2 = compare_fairly(gt_pddl, locm_clean, locm_out_path, learner_type="Full Model (FSM-based)")
    eval_fastlas = compare_fairly(gt_pddl, fastlas_clean, fastlas_out_path, learner_type="Preconditions Only (ASP/ILP)")

    results = {
        "FAMA": eval_fama,
        "LOCM2": eval_locm2,
        "FastLAS": eval_fastlas
    }
    
    with open("benchmark_outputs/phase2_evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*115)
    print("PHASE 2 EMPIRICAL BENCHMARK COMPARISON TABLE (VERIFIED NATIVE RUNS)")
    print("="*115)
    header = f"{'Learner':<10} | {'Paradigm':<28} | {'Actions':<8} | {'PDDL':<7} | {'d_tri':<6} | {'Pre F1':<8} | {'Eff F1':<8} | {'A_appl':<8} | {'A_pred':<8}"
    print(header)
    print("-" * 115)
    for name, ev in results.items():
        act_str = f"{ev['num_learned_actions']}/{ev['num_gt_actions']}"
        val_str = "VALID" if ev['pddl_valid'] else "INVALID"
        pre_f1 = ev['preconditions']['f1']
        eff_f1 = ev['effects']['f1']
        d_tri = ev['d_triangle']
        a_appl = ev['a_appl']
        a_pred = ev['a_pred']
        paradigm = ev['learner_type']
        print(f"{name:<10} | {paradigm:<28} | {act_str:<8} | {val_str:<7} | {d_tri:<6} | {pre_f1:<8.3f} | {eff_f1:<8.3f} | {a_appl:<8.3f} | {a_pred:<8.3f}")
    print("="*115)

    print("\nDetailed Per-Action Breakdown:")
    for name, ev in results.items():
        print(f"\n--- {name} ({ev['learner_type']}) ---")
        for act, data in ev['action_breakdown'].items():
            pre = data['preconditions']
            eff = data['effects']
            print(f"  Action '{act}':")
            print(f"    Preconditions (F1={pre['f1']:.2f}, TP={pre['tp']}, FP={pre['fp']}, FN={pre['fn']}):")
            print(f"      Learned: {pre['learned']}")
            print(f"      GT:      {pre['gt']}")
            print(f"    Effects (F1={eff['f1']:.2f}, TP={eff['tp']}, FP={eff['fp']}, FN={eff['fn']}):")
            print(f"      Learned: {eff['learned']}")
            print(f"      GT:      {eff['gt']}")
            print(f"    d_triangle: {data['d_triangle']}")

    print("\nPassive Transition Prediction Breakdown (Over 100 Observed Steps):")
    for name, ev in results.items():
        t_eval = ev['transition_evaluation']
        print(f"\n--- {name} ---")
        print(f"  Overall A_pred: {t_eval['a_pred']:.4f} ({t_eval['correct_transitions']}/{t_eval['total_transitions']})")
        print(f"  Overall A_appl: {t_eval['a_appl']:.4f} ({t_eval['applicable_transitions']}/{t_eval['total_transitions']})")
        for act, st in t_eval['per_action_stats'].items():
            print(f"    {act:<10}: Correct Next State = {st['correct']}/{st['total']} (Applicable = {st['applicable']}/{st['total']})")

if __name__ == "__main__":
    run_phase2()
