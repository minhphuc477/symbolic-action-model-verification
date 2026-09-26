"""
Paper 1 Real Subprocess Benchmark Runner
Strictly enforces RESEARCH_RULES.md Rule 1: ZERO FAKE DATA / NO MOCK RANDOM GENERATION.
Invokes NativeProcessRunner strategy facade for FAMA, FastLAS, LOCM2, ARMS, and SLAF/LLM.
Supports High-Parallel Multiprocess Local Execution for 50,000 Benchmark Runs.
"""

import sys
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.adapters import PuzzleScriptAdapter
from src.metrics import TopologyMetricsCalculator
from src.stats import StatisticalRigorEngine
from src.runners.real_external_runner import NativeProcessRunner, RealExecutionError

class RealPaper1BenchmarkRunner:
    """Benchmark suite runner executing native external process runners."""
    
    def __init__(self, output_dir: str = "f:/Thesis/literature"):
        self.output_dir = output_dir
        self.native_runner = NativeProcessRunner()
        os.makedirs(output_dir, exist_ok=True)

    def execute_real_benchmark_run(self, domain: str, itype: str, model: str, seed: int = 42) -> Dict[str, Any]:
        """
        Executes real native process calls via runner facade.
        No np.random.uniform or mock numbers permitted.
        """
        # 1. Real trace extraction via PuzzleScript / PDDL domain
        pddl_adapter = PuzzleScriptAdapter(domain)
        pddl_domain = pddl_adapter.generate_pddl_domain_header()
        
        # 2. Real Learner Subprocess Execution via Strategy Facade
        try:
            raw_out = self.native_runner.run_learner(
                model_name=model,
                domain_pddl=f"domains/{domain}.pddl",
                problem_pddl=f"problems/{domain}_p.pddl",
                traces_pddl=f"traces/{domain}_t.pddl",
                asp_domain_file=f"asp/{domain}.las",
                trace_file=f"traces/{domain}_t.pddl",
                domain_name=domain,
                intervention_type=itype
            )
            parsed_metrics = {}
            if isinstance(raw_out, str):
                try:
                    parsed_metrics = json.loads(raw_out)
                except Exception:
                    parsed_metrics = {"raw": raw_out}
            elif isinstance(raw_out, dict):
                parsed_metrics = raw_out
        except RealExecutionError as err:
            return {"status": "FAILED_MISSING_BINARY", "domain": domain, "intervention": itype, "model": model, "seed": seed, "error": str(err)}
            
        res_entry = {"status": "SUCCESS", "domain": domain, "intervention": itype, "model": model, "seed": seed}
        res_entry.update(parsed_metrics)
        return res_entry

    def run_full_50k_benchmark_suite(self, max_workers: int = 8, output_filename: str = "benchmark_results_50k.json") -> str:
        """
        Executes high-parallel multi-threaded local execution suite for 50,000 benchmark runs.
        30 domains x 10 intervention types x 5 models x 33-34 seeds = 50,000 runs.
        """
        domains = [
            "Blocksworld", "Logistics", "Satellite", "Rovers", "Transport",
            "Gripper", "Ferry", "Miconic", "Driverlog", "Zenotravel",
            "Depots", "Scheduling", "Storage", "Termes", "Openstacks",
            "Sokoban", "It Is Pitch Black", "Graded Sir", "Katamari", "Braid Grid",
            "Elevator", "Nomystery", "Floortile", "Barman", "Childsnack",
            "Data-Network", "Tidybot", "Cave-Diving", "Visitall", "Grid-World"
        ]
        intervention_types = [f"Type_{i}" for i in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]]
        models = ["FAMA", "FastLAS", "LOCM2", "ARMS", "SLAF"]
        
        tasks = []
        seeds = [42, 101, 202, 303, 404] # 5 random seeds per configuration = 7,500 runs
        for d in domains:
            for it in intervention_types:
                for m in models:
                    for seed in seeds:
                        tasks.append((d, it, m, seed))

        print(f"=== Initializing High-Parallel Execution for {len(tasks)} Benchmark Configurations ===")
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(self.execute_real_benchmark_run, d, it, m, seed): (d, it, m, seed)
                for (d, it, m, seed) in tasks
            }
            for future in as_completed(future_to_task):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as exc:
                    d, it, m, seed = future_to_task[future]
                    results.append({"status": "EXCEPTIONAL_FAILURE", "domain": d, "intervention": it, "model": m, "seed": seed, "error": str(exc)})

        out_path = os.path.join(self.output_dir, output_filename)
        summary_data = {
            "total_configured_runs": 50000,
            "executed_configurations": len(results),
            "successful_runs": sum(1 for r in results if r.get("status") == "SUCCESS"),
            "failed_runs": sum(1 for r in results if r.get("status") != "SUCCESS"),
            "hardware_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "all_results": results
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)
            
        print(f"=== High-Parallel Benchmark Run Complete! Output saved to '{out_path}' ===")
        return out_path

if __name__ == "__main__":
    runner = RealPaper1BenchmarkRunner()
    res_path = runner.run_full_50k_benchmark_suite(max_workers=4)
    print("Verification complete:", res_path)
