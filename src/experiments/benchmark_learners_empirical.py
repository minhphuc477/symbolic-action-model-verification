"""
benchmark_learners_empirical.py
Measures exact empirical execution runtimes of LOCM2, FastLAS, and FAMA with realistic trace counts.
Strictly adheres to RESEARCH_RULES.md: zero fake metrics, fully deterministic.
"""

import time
import os
import sys
import subprocess

def test_fastlas():
    print("--- 1. BENCHMARKING FASTLAS (ASP Abduction) ---")
    las_file = "/mnt/f/Thesis/test_fastlas.las"
    cmd = ["/usr/local/bin/FastLAS", las_file]
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    print(f"FastLAS Command: {' '.join(cmd)}")
    print(f"FastLAS Return Code: {res.returncode}")
    print(f"FastLAS Runtime: {elapsed:.3f}s")
    print(f"FastLAS Learned Rules:\n{res.stdout.strip()}")
    return elapsed, res.returncode, res.stdout

def test_locm2():
    print("\n--- 2. BENCHMARKING LOCM2 (FSM Induction) ---")
    cmd = ["/mnt/f/Thesis/venv_linux/bin/python", "/mnt/f/Thesis/locm_repo/locm2.py"]
    t0 = time.time()
    res = subprocess.run(cmd, cwd="/mnt/f/Thesis/locm_repo", capture_output=True, text=True)
    elapsed = time.time() - t0
    print(f"LOCM2 Command: {' '.join(cmd)}")
    print(f"LOCM2 Return Code: {res.returncode}")
    print(f"LOCM2 Runtime: {elapsed:.3f}s")
    lines = res.stdout.strip().split("\n")
    print(f"LOCM2 Output Summary (last 3 lines):\n" + "\n".join(lines[-3:]))
    return elapsed, res.returncode, res.stdout

def test_fama():
    print("\n--- 3. BENCHMARKING FAMA (SAT Compilation via Madagascar) ---")
    from meta_planning import dataset, LearningTask
    
    domain = 'blocks'
    m_ref = dataset.load_model(domain)
    m = m_ref.observe(precondition_observability=0, effect_observability=0)
    
    timings = {}
    for n_traces in [1, 5, 10]:
        t0 = time.time()
        T = dataset.load_trajectories(domain, select=range(n_traces))
        O = [t.observe(1.0, action_observability=1, goal_observability=1) for t in T]
        task = LearningTask(m, O)
        sol = task.learn()
        elapsed = time.time() - t0
        timings[n_traces] = elapsed
        print(f"FAMA Trace Count n={n_traces:2d} -> Runtime: {elapsed:.3f}s | Solved: {sol.solution_found}")
    return timings

if __name__ == "__main__":
    t_fastlas, rc_fl, out_fl = test_fastlas()
    t_locm, rc_lm, out_lm = test_locm2()
    fama_timings = test_fama()
    
    print("\n=======================================================")
    print("SUMMARY OF EMPIRICAL LEARNER BENCHMARK:")
    print(f"FastLAS (40 positive+negative examples): {t_fastlas:.3f}s")
    print(f"LOCM2   (full Blocksworld trace log):     {t_locm:.3f}s")
    print(f"FAMA    (SAT compilation n=1 trace):      {fama_timings.get(1, 0):.3f}s")
    print(f"FAMA    (SAT compilation n=5 traces):     {fama_timings.get(5, 0):.3f}s")
    print(f"FAMA    (SAT compilation n=10 traces):    {fama_timings.get(10, 0):.3f}s")
    print("=======================================================")
