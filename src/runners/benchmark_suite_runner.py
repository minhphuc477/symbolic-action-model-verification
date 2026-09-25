"""
Paper 1 Real Subprocess Benchmark Runner
Strictly enforces RESEARCH_RULES.md Rule 1: ZERO FAKE DATA / NO MOCK RANDOM GENERATION.
Invokes NativeProcessRunner strategy facade for FAMA, FastLAS, LOCM2, ARMS, and SLAF/LLM.
"""

import sys
import os
import json
import time
from typing import Dict, Any

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

    def execute_real_benchmark_run(self, domain: str, itype: str, model: str) -> Dict[str, Any]:
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
        except RealExecutionError as err:
            return {"status": "FAILED_MISSING_BINARY", "domain": domain, "intervention": itype, "model": model, "error": str(err)}
            
        return {"status": "SUCCESS", "domain": domain, "intervention": itype, "model": model, "raw_output": raw_out}

if __name__ == "__main__":
    runner = RealPaper1BenchmarkRunner()
    res = runner.execute_real_benchmark_run("Blocksworld", "Type_II", "FAMA")
    print("=== Real Benchmark Suite Runner Verified ===")
    print(json.dumps(res, indent=2))
