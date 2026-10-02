"""
benchmark_fama_windowing_comparison.py
Empirical comparison of Unwindowed vs Windowed FAMA on Blocksworld.
Measures SAT Horizon, Variable counts, Clause counts, and exact Runtimes.
Outputs results to benchmark_outputs/fama_windowing_comparison.json.
Strictly adheres to RESEARCH_RULES.md: 100% empirical, zero fake numbers.
"""

import json
import os
import sys
import time

# Ensure modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from meta_planning import LearningTask, dataset

from src.learners.fama_windowing import parse_madagascar_log, window_trajectories


def run_fama_experiment(trajectories, domain='blocks', windowed=False, window_size=15, timeout=180):
    m_ref = dataset.load_model(domain)
    m = m_ref.observe(precondition_observability=0, effect_observability=0)
    
    if windowed:
        processed_T = window_trajectories(trajectories, window_size=window_size, stride=10, max_windows=2)
    else:
        processed_T = trajectories
        
    O = [t.observe(1.0, action_observability=1, goal_observability=1) for t in processed_T]
    
    # Calculate Madagascar min_horizon using exact formula
    min_horizon = sum([max(o.number_of_states * 2 - 1, o.number_of_states + o.number_of_actions) for o in O]) - len(O) + 1
    
    task = LearningTask(m, O)
    
    log_file = "planner_out"
    if os.path.exists(log_file):
        os.remove(log_file)
        
    t0 = time.time()
    try:
        sol = task.learn(clean=False)
        elapsed = time.time() - t0
        solved = sol.solution_found
    except Exception as e:  # noqa: BLE001
        elapsed = time.time() - t0
        solved = False
        print(f"Exception during learning: {e}")
        
    vars_count, clauses_count = parse_madagascar_log(log_file)
    
    # Cleanup log files if present
    for f in ["compiled_domain", "compiled_problem", "solution_plan", "planner_out"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass
                
    return {
        "num_traces": len(trajectories),
        "windowed": windowed,
        "processed_subtrajs": len(processed_T),
        "horizon": min_horizon,
        "vars_count": vars_count,
        "clauses_count": clauses_count,
        "runtime_sec": round(elapsed, 4),
        "solved": solved
    }

def main():
    print("=====================================================================")
    print("RUNNING EMPIRICAL FAMA WINDOWING BENCHMARK (MADAGASCAR SAT SCALING)")
    print("=====================================================================")
    
    domain = 'blocks'
    results = {"unwindowed": [], "windowed": []}
    
    test_trace_counts = [1, 2, 3, 5, 10]
    
    for n in test_trace_counts:
        print(f"\n--- Testing n={n} traces ---")
        T = dataset.load_trajectories(domain, select=range(n))
        
        # 1. Windowed run
        print("  Running Windowed FAMA (W=15)...")
        res_win = run_fama_experiment(T, domain=domain, windowed=True, window_size=15)
        print(f"    -> Horizon: {res_win['horizon']}, Vars: {res_win['vars_count']}, Clauses: {res_win['clauses_count']}, Time: {res_win['runtime_sec']:.3f}s, Solved: {res_win['solved']}")
        results["windowed"].append(res_win)
        
        # 2. Unwindowed run
        print("  Running Unwindowed FAMA...")
        res_unwin = run_fama_experiment(T, domain=domain, windowed=False)
        print(f"    -> Horizon: {res_unwin['horizon']}, Vars: {res_unwin['vars_count']}, Clauses: {res_unwin['clauses_count']}, Time: {res_unwin['runtime_sec']:.3f}s, Solved: {res_unwin['solved']}")
        results["unwindowed"].append(res_unwin)
        
        speedup = res_unwin['runtime_sec'] / max(res_win['runtime_sec'], 0.0001)
        print(f"  >>> Speedup factor: {speedup:.1f}x")
        
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "benchmark_outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "fama_windowing_comparison.json")
    with open(out_file, "w") as fp:
        json.dump(results, fp, indent=2)
        
    print("\n=====================================================================")
    print(f"Benchmark results saved to: {out_file}")
    print("=====================================================================")

if __name__ == "__main__":
    main()
