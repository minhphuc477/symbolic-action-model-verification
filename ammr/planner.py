"""Classical planning wrappers: Fast Downward (via WSL / Linux) and pure-Python A*/BFS."""

from __future__ import annotations

import heapq
import json
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Protocol

from ammr.pddl.io import write_domain, write_problem
from ammr.pddl.model import Domain, GroundAction, Problem, State, ground_actions


class PlanStatus(StrEnum):
    SOLVED = "solved"
    UNSOLVABLE = "unsolvable"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass(frozen=True)
class PlanResult:
    status: PlanStatus
    plan: tuple[GroundAction, ...] = ()
    elapsed_s: float = 0.0
    detail: str = ""


class Planner(Protocol):
    def solve(self, domain: Domain, problem: Problem, timeout_s: float = 15.0) -> PlanResult: ...


def validate_plan(domain: Domain, problem: Problem, plan: Sequence[GroundAction]) -> bool:
    """Return True iff ``plan`` is applicable step-by-step from ``init`` and reaches ``goal``."""
    state: State = problem.init
    for act_name, args in plan:
        schema = domain.actions.get(act_name)
        if schema is None or not schema.is_applicable(state, args):
            return False
        state = schema.successor(state, args)
    return problem.goal_reached(state)


class PythonBFSPlanner:
    """Deterministic pure-Python greedy/A* forward planner for unit tests and small tasks."""

    def __init__(self, max_expansions: int = 25_000) -> None:
        self.max_expansions = max_expansions

    def solve(self, domain: Domain, problem: Problem, timeout_s: float = 10.0) -> PlanResult:
        t0 = time.perf_counter()
        if problem.goal_reached(problem.init):
            return PlanResult(PlanStatus.SOLVED, (), time.perf_counter() - t0)
        actions = list(ground_actions(domain, problem))

        def _h(s: State) -> int:
            return len(problem.goal_pos - s) + len(problem.goal_neg & s)

        counter = 0
        pq: list[tuple[int, int, int, State, tuple[GroundAction, ...]]] = [
            (_h(problem.init), 0, counter, problem.init, ())
        ]
        best_g: dict[State, int] = {problem.init: 0}
        expansions = 0

        while pq:
            if time.perf_counter() - t0 > timeout_s or expansions >= self.max_expansions:
                return PlanResult(PlanStatus.TIMEOUT, (), time.perf_counter() - t0)
            _, g, _, state, path = heapq.heappop(pq)
            if g > best_g.get(state, g):
                continue
            expansions += 1
            for act_name, args in actions:
                schema = domain.actions[act_name]
                if not schema.is_applicable(state, args):
                    continue
                nxt = schema.successor(state, args)
                new_plan = (*path, (act_name, args))
                if problem.goal_reached(nxt):
                    return PlanResult(PlanStatus.SOLVED, new_plan, time.perf_counter() - t0)
                ng = g + 1
                if ng < best_g.get(nxt, ng + 1):
                    best_g[nxt] = ng
                    counter += 1
                    heapq.heappush(pq, (ng + _h(nxt), ng, counter, nxt, new_plan))

        return PlanResult(PlanStatus.UNSOLVABLE, (), time.perf_counter() - t0)


_WSL_DAEMON = """
import glob, json, os, shutil, subprocess, sys, tempfile
work = tempfile.mkdtemp(prefix="ammr_fd_")
try:
    for line in sys.stdin:
        req = json.loads(line)
        dp, pp = f"{work}/d.pddl", f"{work}/p.pddl"
        pl, sas = f"{work}/plan", f"{work}/out.sas"
        for old in glob.glob(f"{pl}*") + [sas]:
            if os.path.exists(old):
                os.remove(old)
        with open(dp, "w", encoding="utf-8") as f:
            f.write(req["domain"])
        with open(pp, "w", encoding="utf-8") as f:
            f.write(req["problem"])
        try:
            proc = subprocess.run(
                [
                    "python3", req["fd_bin"], "--sas-file", sas, "--plan-file", pl,
                    dp, pp, "--search", req["search"],
                ],
                capture_output=True, text=True, timeout=req["timeout"],
            )
            pfiles = sorted(glob.glob(f"{pl}*"))
            plan_txt = open(pfiles[-1], encoding="utf-8").read() if pfiles else ""
            resp = {"rc": proc.returncode, "plan": plan_txt, "err": proc.stderr[-300:]}
        except subprocess.TimeoutExpired:
            resp = {"rc": -1, "plan": "", "err": "timeout"}
        print(json.dumps(resp), flush=True)
finally:
    shutil.rmtree(work, ignore_errors=True)
"""


def _parse_fd_plan(text: str) -> tuple[GroundAction, ...]:
    steps: list[GroundAction] = []
    for raw in text.splitlines():
        line = raw.strip().lower()
        if line.startswith("(") and line.endswith(")"):
            parts = line[1:-1].split()
            if parts:
                steps.append((parts[0], tuple(parts[1:])))
    return tuple(steps)


class FastDownwardPlanner:
    """Persistent Fast Downward planner executing inside Linux / WSL ``/tmp``."""

    def __init__(
        self,
        search: str = "astar(lmcut())",
        fd_bin: str = "/opt/downward/fast-downward.py",
    ) -> None:
        self.search = search
        self.fd_bin = fd_bin
        self._proc: subprocess.Popen[str] | None = None

    def _ensure_proc(self) -> subprocess.Popen[str]:
        if self._proc is None or self._proc.poll() is not None:
            cmd = (
                ["wsl", "-d", "Ubuntu", "--", "python3", "-c", _WSL_DAEMON]
                if sys.platform == "win32"
                else ["python3", "-c", _WSL_DAEMON]
            )
            self._proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
        return self._proc

    def close(self) -> None:
        if self._proc is not None:
            if self._proc.stdin:
                self._proc.stdin.close()
            self._proc.terminate()
            self._proc = None

    def __enter__(self) -> FastDownwardPlanner:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def solve(self, domain: Domain, problem: Problem, timeout_s: float = 15.0) -> PlanResult:
        t0 = time.perf_counter()
        proc = self._ensure_proc()
        # Some benchmark files spell the domain name differently in the problem header
        # (e.g. AMLGym visitall: grid-visit-all vs grid_visit_all); FD rejects mismatches.
        aligned = replace(problem, domain_name=domain.name)
        payload = json.dumps(
            {
                "domain": write_domain(domain),
                "problem": write_problem(aligned),
                "search": self.search,
                "fd_bin": self.fd_bin,
                "timeout": timeout_s,
            }
        )
        assert proc.stdin is not None and proc.stdout is not None
        proc.stdin.write(payload + "\n")
        proc.stdin.flush()
        raw = proc.stdout.readline()
        elapsed = time.perf_counter() - t0
        if not raw:
            self.close()
            return PlanResult(PlanStatus.ERROR, (), elapsed, "FD worker closed unexpectedly")
        resp = json.loads(raw)
        rc = int(resp["rc"])
        plan = _parse_fd_plan(resp["plan"])
        if rc == 0 and (plan or problem.goal_reached(problem.init)):
            return PlanResult(PlanStatus.SOLVED, plan, elapsed)
        if rc == -1 or rc in (22, 23):
            return PlanResult(PlanStatus.TIMEOUT, (), elapsed, resp["err"])
        if rc in (11, 12):
            return PlanResult(PlanStatus.UNSOLVABLE, (), elapsed, resp["err"])
        return PlanResult(PlanStatus.ERROR, (), elapsed, f"rc={rc}: {resp['err']}")
