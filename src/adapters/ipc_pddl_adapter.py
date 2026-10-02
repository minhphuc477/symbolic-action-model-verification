"""
IPC PDDL Domain & Trace Adapter Module
======================================
Loads genuine PDDL domains from the `domains/` directory and extracts real
action traces from problem instances and valid execution plans.
Strictly adheres to RESEARCH_RULES.md: ZERO synthetic/mock traces.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple


class IPCPDDLAdapter:
    """
    Adapter for genuine IPC benchmarks and game domains.
    Reads verified PDDL domain/problem files from disk and generates valid traces.
    """

    def __init__(self, domain_name: str, domains_root: str = "domains"):
        self.domain_name = domain_name.lower()
        self.domains_root = Path(domains_root)

    def get_domain_pddl_path(self) -> Path:
        """Locates the genuine PDDL domain file on disk."""
        path = self.domains_root / self.domain_name / "domain.pddl"
        if not path.exists():
            raise FileNotFoundError(
                f"Ground-truth PDDL domain not found for '{self.domain_name}' at {path}. "
                "Ensure domain files are placed in domains/<domain_name>/domain.pddl."
            )
        return path

    def get_problem_pddl_path(self, problem_id: str = "problem_p01") -> Path:
        """Locates the genuine PDDL problem file on disk."""
        path = self.domains_root / self.domain_name / f"{problem_id}.pddl"
        if not path.exists():
            raise FileNotFoundError(
                f"Ground-truth PDDL problem not found for '{self.domain_name}' at {path}."
            )
        return path

    def load_domain_text(self) -> str:
        """Reads and returns the ground-truth PDDL domain definition."""
        return self.get_domain_pddl_path().read_text(encoding="utf-8")

    def load_problem_text(self, problem_id: str = "problem_p01") -> str:
        """Reads and returns the ground-truth PDDL problem definition."""
        return self.get_problem_pddl_path(problem_id).read_text(encoding="utf-8")

    def generate_ground_truth_traces(
        self,
        problem_id: str = "problem_p01",
        max_steps: int = 100,
    ) -> Dict[str, Any]:
        """
        Executes genuine plan actions via Fast Downward / Forward Planner
        to collect verified (s_t, a_t, s_{t+1}) transition traces.
        """
        import pddl
        from src.metrics.transition_accuracy import parse_pddl_model
        from src.runners.wsl_harness import FastDownwardRunner

        dom_path = self.get_domain_pddl_path()
        prob_path = self.get_problem_pddl_path(problem_id)

        # 1. Solve with Fast Downward to get optimal execution plan
        runner = FastDownwardRunner()
        sol_file = str(self.domains_root / "trace_plan.soln")
        res = runner.plan(str(dom_path), str(prob_path), sol_file)

        if not res.success or not os.path.exists(sol_file):
            return {
                "domain": self.domain_name,
                "problem": problem_id,
                "num_traces": 0,
                "traces": [],
                "error": f"Planner failed: {res.error_message}",
            }

        # 2. Parse plan actions
        plan_actions = []
        with open(sol_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("(") and not line.startswith(";"):
                    plan_actions.append(line)

        # 3. Simulate step-by-step on true physics
        actions_map = parse_pddl_model(self.load_domain_text())
        prob = pddl.parse_problem(str(prob_path))
        cur_state = set(str(x) for x in prob.init)

        trace_steps = []
        for idx, act_str in enumerate(plan_actions[:max_steps]):
            clean = act_str.strip("()")
            parts = clean.split()
            act_name = parts[0].lower()
            args = [p.lower() for p in parts[1:]]

            schema = actions_map.get(act_name)
            if not schema:
                break

            pmap = {p: a for p, a in zip(schema.params, args)}
            next_state = schema.apply(cur_state, pmap)
            if next_state is None:
                break

            trace_steps.append({
                "step": idx + 1,
                "action": act_str,
                "state_before": sorted(list(cur_state)),
                "state_after": sorted(list(next_state)),
            })
            cur_state = next_state

        return {
            "domain": self.domain_name,
            "problem": problem_id,
            "plan_length": len(plan_actions),
            "num_steps": len(trace_steps),
            "trace": trace_steps,
        }


if __name__ == "__main__":
    adapter = IPCPDDLAdapter("blocksworld")
    print(f"Domain text loaded ({len(adapter.load_domain_text())} chars)")
    traces_data = adapter.generate_ground_truth_traces()
    print(f"Extracted {traces_data.get('num_steps', 0)} verified trace steps from native Fast Downward execution.")
