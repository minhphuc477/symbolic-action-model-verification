"""
run_phase2_benchmarks.py
End-to-End benchmark runner for Phase 2:
1. Runs FAMA, LOCM2, and FastLAS on Blocksworld.
2. Applies translators/cleaners:
   - fama_cleaner.py
   - locm2_translator.py
   - fastlas_translator.py
3. Compares all 3 normalized action models against Ground Truth PDDL.
4. Reports real, non-mocked d_triangle, Precision, Recall, and A_pred.
"""

import os
import subprocess
import json
from src.adapters.fama_cleaner import clean_fama_pddl
from src.adapters.locm2_translator import translate_locm2_file
from src.adapters.fastlas_translator import translate_fastlas_rules_to_pddl
from src.metrics.model_comparator import compare_action_models

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
    # Extract learned PDDL block
    if "LEARNED PDDL DOMAIN MODEL:" in fama_stdout:
        fama_raw_pddl = fama_stdout.split("LEARNED PDDL DOMAIN MODEL:")[1].strip()
    else:
        fama_raw_pddl = fama_stdout.strip()
    fama_clean = clean_fama_pddl(fama_raw_pddl)
    with open("benchmark_outputs/fama_normalized.pddl", "w", encoding="utf-8") as f:
        f.write(fama_clean)
    print("FAMA Normalized PDDL saved.")

    print("\n=== Step 2: Running & Translating LOCM2 ===")
    locm_cmd = 'wsl bash -c "cd /mnt/f/Thesis/locm_repo && /mnt/f/Thesis/venv_linux/bin/python locm2.py"'
    subprocess.run(locm_cmd, shell=True, capture_output=True, text=True)
    locm_raw_path = "locm_repo/output/Blocksworld/Blocksworld.pddl"
    locm_clean = translate_locm2_file(locm_raw_path, "benchmark_outputs/locm2_normalized.pddl")
    print("LOCM2 Normalized PDDL saved.")

    print("\n=== Step 3: Running & Translating FastLAS ===")
    fastlas_cmd = 'wsl bash -c "FastLAS /mnt/f/Thesis/test_fastlas.las"'
    res_fastlas = subprocess.run(fastlas_cmd, shell=True, capture_output=True, text=True)
    fastlas_rules = res_fastlas.stdout.strip()
    fastlas_clean = translate_fastlas_rules_to_pddl(fastlas_rules)
    with open("benchmark_outputs/fastlas_normalized.pddl", "w", encoding="utf-8") as f:
        f.write(fastlas_clean)
    print("FastLAS Normalized PDDL saved.")

    print("\n=== Step 4: Comparing with Ground Truth ===")
    eval_fama = compare_action_models(gt_pddl, fama_clean)
    eval_locm2 = compare_action_models(gt_pddl, locm_clean)
    eval_fastlas = compare_action_models(gt_pddl, fastlas_clean)

    results = {
        "FAMA": eval_fama,
        "LOCM2": eval_locm2,
        "FastLAS": eval_fastlas
    }
    
    with open("benchmark_outputs/phase2_evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*70)
    print("PHASE 2 EMPIRICAL BENCHMARK COMPARISON TABLE")
    print("="*70)
    print(f"{'Learner':<10} | {'Actions':<8} | {'d_triangle':<12} | {'Precision':<10} | {'Recall':<10} | {'A_pred':<10} | {'F1':<10}")
    print("-" * 75)
    for name, ev in results.items():
        act_str = f"{ev['num_learned_actions']}/{ev['num_gt_actions']}"
        print(f"{name:<10} | {act_str:<8} | {ev['d_triangle']:<12} | {ev['precision']:<10.3f} | {ev['recall']:<10.3f} | {ev['a_pred']:<10.3f} | {ev['f1']:<10.3f}")
    print("="*70)

if __name__ == "__main__":
    run_phase2()
