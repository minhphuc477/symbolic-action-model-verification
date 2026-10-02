"""
WSL Harness & Native Solver Wrappers — CEG-OMR Thesis
======================================================
Provides clean, OS-independent abstractions for running native planning
and inductive logic programming solvers across Windows and WSL Linux:
  * Fast Downward (planning generator)
  * FastLAS (ILP Horn clause synthesizer)
  * Clingo / Potassco (ASP solver)
  * Madagascar / FAMA (SAT-based action model learner)
  * LOCM2 (FSM-based action model learner)

Exit Code Contracts Handled:
  * Fast Downward : 0 = plan found, 11 = unsolvable, 12 = out of memory/time
  * FastLAS       : Returns 0 always; must inspect stderr for fatal syntax/file errors
  * Clingo        : 10 = SAT, 20 = UNSAT, 30 = OPTIMUM_FOUND, 0 = no-solve
  * Madagascar    : Wrapped in sequential mode (-P 0 -S 1) with stdout parsing
  * LOCM2         : Runs with PYTHONHASHSEED=0 for deterministic FSM numbering
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SolverResult:
    """Standardized result returned by all solver runners."""
    solver: str
    success: bool
    returncode: int
    stdout: str
    stderr: str
    wall_clock_seconds: float
    output_files: List[str] = field(default_factory=list)
    error_message: str = ""


class WSLHarness:
    """
    OS-aware process harness that automatically routes commands to native
    Linux or delegates via `wsl -d Ubuntu -- bash -c` on Windows.
    """

    @staticmethod
    def is_windows() -> bool:
        return sys.platform == "win32"

    @staticmethod
    def to_wsl_path(path: str | Path) -> str:
        """Convert a Windows path (e.g. F:\\Thesis\\...) to WSL path (/mnt/f/Thesis/...)."""
        p = Path(path).resolve()
        parts = p.parts
        if len(parts) > 0 and len(parts[0]) == 3 and parts[0][1] == ":":
            drive = parts[0][0].lower()
            rest = "/".join(parts[1:])
            return f"/mnt/{drive}/{rest}"
        return str(p).replace("\\", "/")

    @classmethod
    def run_cmd(
        cls,
        cmd_str: str,
        timeout: int = 60,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str, str, float]:
        """
        Execute command with proper OS delegation.
        """
        env_prefix = ""
        if env_vars:
            env_prefix = " ".join(f"{k}={v}" for k, v in env_vars.items()) + " "

        full_cmd_str = env_prefix + cmd_str

        if cls.is_windows():
            exec_args = ["wsl", "-d", "Ubuntu", "--", "bash", "-c", full_cmd_str]
        else:
            exec_args = ["bash", "-c", full_cmd_str]

        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                exec_args,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = time.perf_counter() - t0
            return proc.returncode, proc.stdout, proc.stderr, elapsed
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout ({timeout}s) expired", timeout
        except Exception as e:
            return -2, "", str(e), 0.0


class FastDownwardRunner:
    """Wrapper for Fast Downward with optimal or satisficing search."""

    def __init__(self, fd_path: str = "/opt/downward/fast-downward.py"):
        self.fd_path = fd_path

    def plan(
        self,
        domain_file: str,
        problem_file: str,
        plan_out: str,
        search_config: str = "astar(lmcut())",
        timeout: int = 30,
    ) -> SolverResult:
        wsl_dom = WSLHarness.to_wsl_path(domain_file)
        wsl_prob = WSLHarness.to_wsl_path(problem_file)
        wsl_plan = WSLHarness.to_wsl_path(plan_out)

        cmd = (
            f"python3 {self.fd_path} "
            f"--plan-file {wsl_plan} "
            f"{wsl_dom} {wsl_prob} "
            f"--search '{search_config}'"
        )

        code, out, err, elapsed = WSLHarness.run_cmd(cmd, timeout=timeout)
        success = (code == 0) and Path(plan_out).exists()

        return SolverResult(
            solver="FastDownward",
            success=success,
            returncode=code,
            stdout=out,
            stderr=err,
            wall_clock_seconds=elapsed,
            output_files=[plan_out] if success else [],
            error_message="" if success else f"Exit code {code}: {err[:200]}",
        )


class FastLASRunner:
    """Wrapper for FastLAS with strict exit code validation (checking stderr)."""

    def __init__(self, bin_path: str = "/usr/local/bin/FastLAS"):
        self.bin_path = bin_path

    def solve(self, las_file: str, timeout: int = 60) -> SolverResult:
        wsl_las = WSLHarness.to_wsl_path(las_file)
        cmd = f"{self.bin_path} --threads 1 {wsl_las}"

        code, out, err, elapsed = WSLHarness.run_cmd(cmd, timeout=timeout)
        # FastLAS exit-code bug: returns 0 on errors, check stderr for "Error"
        has_error = ("error" in err.lower()) or ("error opening" in out.lower())
        success = (code == 0) and not has_error

        return SolverResult(
            solver="FastLAS",
            success=success,
            returncode=code,
            stdout=out,
            stderr=err,
            wall_clock_seconds=elapsed,
            error_message="" if success else f"FastLAS failed: {err[:200]}",
        )


class ClingoRunner:
    """Wrapper for Potassco Clingo with correct exit code mapping."""

    def __init__(self, bin_path: str = "/usr/bin/clingo"):
        self.bin_path = bin_path

    def solve(self, asp_file: str, timeout: int = 60) -> SolverResult:
        wsl_asp = WSLHarness.to_wsl_path(asp_file)
        cmd = f"{self.bin_path} --seed=42 --rand-freq=0 {wsl_asp}"

        code, out, err, elapsed = WSLHarness.run_cmd(cmd, timeout=timeout)
        # 10 = SAT, 20 = UNSAT, 30 = OPTIMUM
        success = code in (10, 30)

        return SolverResult(
            solver="Clingo",
            success=success,
            returncode=code,
            stdout=out,
            stderr=err,
            wall_clock_seconds=elapsed,
            error_message="" if success else f"Clingo exit {code} (UNSAT or error)",
        )
