"""
Fast Downward Plan Generator Component
======================================
Wraps Fast Downward via WSLHarness / FastDownwardRunner to compute candidate plans
for the current action model M_hat.
"""

from __future__ import annotations

from pathlib import Path

from src.repair.config import CEGOMRConfig
from src.runners.wsl_harness import FastDownwardRunner


def fd_plan_found(returncode: int, plan_file: Path) -> bool:
    """Check whether Fast Downward exited cleanly and wrote a plan file."""
    return returncode == 0 and plan_file.exists() and plan_file.stat().st_size > 0


class FastDownwardGenerator:
    """
    Wraps Fast Downward (WSL) as the CEG-OMR Generator component.
    Computes candidate optimal plan pi* for M_hat.
    """

    def __init__(self, config: CEGOMRConfig):
        self.config = config

    def generate_plan(
        self,
        domain_path: str,
        problem_path: str,
        plan_out: str,
    ) -> tuple[bool, list[str], float]:
        """
        Run Fast Downward and return (plan_found, actions, elapsed_seconds).
        Returns (False, [], inf) if unsolvable or resources exhausted.

        Exit code conventions: 0 = plan found, 11 = unsolvable, 12 = out of resources.
        """
        runner = FastDownwardRunner(fd_path=self.config.fast_downward_bin)
        res = runner.plan(
            domain_file=domain_path,
            problem_file=problem_path,
            plan_out=plan_out,
            search_config=self.config.fd_search_config,
            timeout=self.config.planning_timeout,
        )

        if not res.success:
            return False, [], float("inf")

        plan_path = Path(plan_out)
        if not plan_path.exists():
            plan_path = Path(plan_out + ".1")
        if not plan_path.exists():
            return False, [], float("inf")

        actions = self._parse_plan_file(plan_path)
        return True, actions, res.wall_clock_seconds

    @staticmethod
    def _parse_plan_file(plan_path: Path) -> list[str]:
        """Parse a Fast Downward plan file into a list of normalized action strings."""
        actions: list[str] = []
        for line in plan_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("(") and not line.startswith("; "):
                actions.append(line)
        return actions


# Backward compatibility alias
_fd_plan_found = fd_plan_found
