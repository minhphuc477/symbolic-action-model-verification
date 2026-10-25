"""
CEG-OMR Configuration and Result Data Structures
================================================
Defines immutable run configurations, counterexample records, and benchmark metrics.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field


@dataclass
class CEGOMRConfig:
    """
    All configuration for one CEG-OMR repair run.
    Immutable after construction.
    """
    domain_path: str               # Path to PDDL domain file (possibly mutated)
    problem_path: str              # Path to PDDL problem file
    ground_truth_domain: str = "" # Path to M* (ground truth) domain; if empty, same as domain_path
    max_repair_iterations: int = 100
    max_environment_steps: int = 100
    seed: int = 42
    # Fast Downward invocation settings
    fast_downward_bin: str = "/opt/downward/fast-downward.py"  # Installed location in WSL
    fd_search_config: str = "astar(lmcut())"
    fd_plan_file: str = "plan.soln"
    # Execution prefix: empty on native Linux/WSL, delegates via wsl on Windows
    wsl_prefix: list[str] = field(default_factory=lambda: [] if sys.platform != "win32" else ["wsl", "-d", "Ubuntu", "--"])
    # Output directory for plans and repair logs
    out_dir: str = "repair_logs/"
    # Timeout per planning call (seconds)
    planning_timeout: int = 30
    # Ablation knobs
    enable_backtracking: bool = True
    use_effect_coherence: bool = True
    allow_relaxation: bool = True
    allow_effect_deletion: bool = True
    max_relaxation_size: int = 3
    max_suspects_per_level: int = 12


@dataclass
class Counterexample:
    """
    A single counterexample tuple xi_t = <s_t, a_t, s_hat_{t+1}, s*_{t+1}>.

    Fields
    ------
    step_index     : int - index t in the candidate plan
    action         : str - the action a_t that failed
    predicted_next : str - what M_hat predicted (s_hat_{t+1})
    actual_next    : str - what M* produced (s*_{t+1}); "FAILURE" if action inapplicable
    failure_type   : str - "phantom_precondition" | "wrong_effect" | "inapplicable"
    current_state  : str - string representation of the state s_t at failure
    """
    step_index: int
    action: str
    predicted_next: str
    actual_next: str
    failure_type: str = "phantom_precondition"
    current_state: str = ""

    def __str__(self) -> str:
        return (
            f"xi_{self.step_index}: action={self.action} | "
            f"predicted={self.predicted_next[:40]}... | "
            f"actual={self.actual_next[:40]}... | type={self.failure_type}"
        )


@dataclass
class CEGOMRResult:
    """
    Complete result of one CEG-OMR repair run.
    All fields are populated from real solver outputs.
    """
    success: bool
    total_queries: int            # K_repair - active env steps used
    iterations: int               # repair loop iterations
    counterexamples: list[Counterexample] = field(default_factory=list)
    repaired_domain_path: str = ""
    play_regret_before: float = float("inf")  # R_play before repair
    play_regret_after: float = 0.0            # R_play after repair (0 = perfect)
    wall_clock_seconds: float = 0.0
    error_message: str = ""
    per_iteration_queries: list[int] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "CEG-OMR Repair Summary",
            "=" * 60,
            f"  Success:           {self.success}",
            f"  K_repair (queries):{self.total_queries}",
            f"  Iterations:        {self.iterations}",
            f"  R_play before:     {self.play_regret_before}",
            f"  R_play after:      {self.play_regret_after}",
            f"  Wall clock:        {self.wall_clock_seconds:.2f}s",
            f"  Repaired domain:   {self.repaired_domain_path or 'N/A'}",
        ]
        if self.counterexamples:
            lines.append(f"  Counterexamples ({len(self.counterexamples)}):")
            for cx in self.counterexamples[:5]:
                lines.append(f"    {cx}")
        if self.error_message:
            lines.append(f"  Error: {self.error_message}")
        lines.append("=" * 60)
        return "\n".join(lines)
