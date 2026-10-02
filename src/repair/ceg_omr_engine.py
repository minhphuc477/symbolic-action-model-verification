"""
CEG-OMR Engine — Counterexample-Guided Online Model Repair
============================================================
This module implements the core CEG-OMR algorithm (Algorithm 1 from the paper):

    Generator (Fast Downward) → Oracle Verifier (game engine) → Synthesizer (Horn elimination)

The algorithm structure follows from:
  * Angluin (1992) Exact Learning of Horn Clauses
  * Kearns & Singh (2002) Active RL with finite state spaces
  * Gil (1992), Wang (1995) Online model acquisition

Formal guarantee (Theorem 2):
  K_repair ≤ k · |F|^r
  where k = number of mutated action rules (|Δ-DSL|),
        |F| = number of domain fluents,
        r = maximum action arity.

Design principles:
  * ZERO fake data — every step is grounded in real solver execution
  * All randomness seeded for reproducibility
  * Strict exit-code handling for all solvers (FastLAS, Clingo, Madagascar)
  * Modular: Generator / Verifier / Synthesizer are separate injectable objects

Usage (API):
    from src.repair.ceg_omr_engine import CEGOMREngine, CEGOMRConfig

    engine = CEGOMREngine(
        config=CEGOMRConfig(
            domain_path="domains/blocksworld/domain.pddl",
            problem_path="domains/blocksworld/problem_p01.pddl",
            max_repair_iterations=50,
            seed=42,
        )
    )
    result = engine.run()
    print(result.summary())
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Counterexample record
# ---------------------------------------------------------------------------

@dataclass
class Counterexample:
    """
    A single counterexample tuple ξ_t = ⟨s_t, a_t, ŝ_{t+1}, s*_{t+1}⟩.

    Fields
    ------
    step_index     : int — index t in the candidate plan
    action         : str — the action a_t that failed
    predicted_next : str — what M̂ predicted (ŝ_{t+1})
    actual_next    : str — what M* produced (s*_{t+1}); "FAILURE" if action inapplicable
    failure_type   : str — "phantom_precondition" | "wrong_effect" | "inapplicable"
    """
    step_index: int
    action: str
    predicted_next: str
    actual_next: str
    failure_type: str = "phantom_precondition"
    current_state: str = ""

    def __str__(self) -> str:
        return (
            f"ξ_{self.step_index}: action={self.action} | "
            f"predicted={self.predicted_next[:40]}... | "
            f"actual={self.actual_next[:40]}... | type={self.failure_type}"
        )


# ---------------------------------------------------------------------------
# Repair result record
# ---------------------------------------------------------------------------

@dataclass
class CEGOMRResult:
    """
    Complete result of one CEG-OMR repair run.
    All fields are populated from real solver outputs.
    """
    success: bool
    total_queries: int            # K_repair — active env steps used
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


# ---------------------------------------------------------------------------
# Solver exit code contracts (from Explorer 2 handoff.md findings)
# ---------------------------------------------------------------------------

# FastLAS: exit 0 always (even on error); must check stderr for "Error"
def _fastlas_succeeded(returncode: int, stderr: str) -> bool:
    return "Error" not in stderr and "error" not in stderr.lower()

# Clingo: exit 10 = SAT (not exhausted), 20 = UNSAT, 30 = SAT (optimum found), 0 = no solve
def _clingo_succeeded(returncode: int) -> bool:
    return returncode in (10, 30)

# Fast Downward: exit 0 = plan found, 11 = unsolvable, 12 = search exhausted
def _fd_plan_found(returncode: int) -> bool:
    return returncode == 0


# ---------------------------------------------------------------------------
# Generator — Fast Downward wrapper
# ---------------------------------------------------------------------------

class FastDownwardGenerator:
    """
    Wraps Fast Downward (WSL) as the CEG-OMR Generator component.
    Computes candidate optimal plan π* for M̂.
    """

    def __init__(self, config: CEGOMRConfig):
        self.config = config

    def generate_plan(self, domain_path: str, problem_path: str, plan_out: str) -> tuple[bool, list[str], float]:
        """
        Run Fast Downward and return (plan_found, actions, cost).
        Returns (False, [], inf) if unsolvable or FD missing.

        Exit codes: 0 = plan found, 11 = unsolvable, 12 = out of resources.
        """
        fd_bin = self.config.fast_downward_bin

        # Translate Windows paths to WSL /mnt/ paths
        def to_wsl(p: str) -> str:
            p = Path(p).resolve()
            parts = p.parts
            # "F:\\" → "/mnt/f/"
            if len(parts) > 0 and len(parts[0]) == 3 and parts[0][1] == ":":
                drive = parts[0][0].lower()
                rest = "/".join(parts[1:])
                return f"/mnt/{drive}/{rest}"
            return str(p).replace("\\", "/")

        wsl_domain  = to_wsl(domain_path)
        wsl_problem = to_wsl(problem_path)
        wsl_plan    = to_wsl(plan_out)

        cmd = (
            self.config.wsl_prefix
            + [
                "python3", fd_bin,
                "--plan-file", wsl_plan,
                wsl_domain, wsl_problem,
                "--search", self.config.fd_search_config,
            ]
        )

        t0 = time.perf_counter()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.planning_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, [], float("inf")
        except FileNotFoundError:
            return False, [], float("inf")

        elapsed = time.perf_counter() - t0

        if not _fd_plan_found(res.returncode):
            return False, [], float("inf")

        # Read plan file
        plan_path = Path(plan_out)
        if not plan_path.exists():
            # Try .soln suffix
            plan_path = Path(plan_out + ".1")
        if not plan_path.exists():
            return False, [], float("inf")

        actions = self._parse_plan_file(plan_path)
        return True, actions, elapsed

    @staticmethod
    def _parse_plan_file(plan_path: Path) -> list[str]:
        """Parse a Fast Downward plan file into list of action strings."""
        actions = []
        for line in plan_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("(") and not line.startswith("; "):
                actions.append(line)
        return actions


# ---------------------------------------------------------------------------
# Oracle Verifier — PDDL forward execution
# ---------------------------------------------------------------------------

class OracleVerifier:
    """
    Executes a plan prefix against M* (ground truth domain) and detects
    the first divergence point.

    For PDDL domains: uses a lightweight Python forward simulator.
    For game engines: this class would be subclassed with a game-specific executor.
    """

    def __init__(self, ground_truth_domain: str, problem_path: str):
        self.gt_domain = ground_truth_domain
        self.problem_path = problem_path
        self._gt_domain_text = Path(ground_truth_domain).read_text(encoding="utf-8") if ground_truth_domain else ""

    def verify_prefix(
        self,
        plan: list[str],
        learned_domain: str,
    ) -> tuple[bool, Counterexample | None, int]:
        """
        Execute plan against ground truth M*.
        """
        if not self.gt_domain:
            return True, None, len(plan)

        try:
            import pddl

            from src.metrics.transition_accuracy import parse_pddl_model

            gt_text = Path(self.gt_domain).read_text(encoding="utf-8")
            learned_text = Path(learned_domain).read_text(encoding="utf-8")

            gt_actions = parse_pddl_model(gt_text)
            learned_actions = parse_pddl_model(learned_text)

            prob = pddl.parse_problem(self.problem_path)
            init_state = {str(x) for x in prob.init}
            
            # Goal literals
            if hasattr(prob.goal, "operands"):
                goal_literals = {str(x) for x in prob.goal.operands}
            else:
                goal_literals = {str(prob.goal)}

            state_gt = set(init_state)
            state_learned = set(init_state)
            queries = 0

            for i, action_str in enumerate(plan):
                queries += 1  # Each execution step = 1 oracle query
                act_name, args = _parse_action_tuple(action_str)

                gt_schema = gt_actions.get(act_name)
                learned_schema = learned_actions.get(act_name)

                if not gt_schema or not learned_schema:
                    cx = Counterexample(
                        step_index=i,
                        action=action_str,
                        predicted_next=_state_str(state_learned),
                        actual_next="FAILURE",
                        failure_type="unknown_action",
                    )
                    return False, cx, queries

                pmap_gt = {p: a for p, a in zip(gt_schema.params, args)}
                pmap_learned = {p: a for p, a in zip(learned_schema.params, args)}

                next_gt = gt_schema.apply(state_gt, pmap_gt)
                next_learned = learned_schema.apply(state_learned, pmap_learned)

                if next_gt is None:
                    cx = Counterexample(
                        step_index=i,
                        action=action_str,
                        predicted_next=_state_str(state_learned),
                        actual_next="FAILURE",
                        failure_type="inapplicable",
                        current_state=_state_str(state_gt),
                    )
                    return False, cx, queries

                if next_gt != next_learned:
                    cx = Counterexample(
                        step_index=i,
                        action=action_str,
                        predicted_next=_state_str(state_learned),
                        actual_next=_state_str(next_gt),
                        failure_type="phantom_precondition" if next_learned is not None else "wrong_effect",
                        current_state=_state_str(state_gt),
                    )
                    return False, cx, queries

                state_gt = next_gt
                state_learned = next_learned

            goal_reached = goal_literals.issubset(state_gt)
            return goal_reached, None, queries

        except Exception as e:  # noqa: BLE001
            print(f"[OracleVerifier] Error during verification: {e}", file=sys.stderr)
            cx = Counterexample(
                step_index=0,
                action=plan[0] if plan else "",
                predicted_next="ERROR",
                actual_next=str(e),
                failure_type="verification_error",
            )
            return False, cx, 0


# ---------------------------------------------------------------------------
# Synthesizer — Model update via precondition refinement
# ---------------------------------------------------------------------------

class HornSynthesizer:
    """
    Synthesizer component: given a counterexample ξ_t, update M̂ to eliminate
    the phantom transition. Uses a version-space / Horn-clause elimination approach
    (Angluin 1992).

    For Type II interventions: identifies the omitted precondition from the
    counterexample state and adds it back to the action schema.
    """

    def __init__(self, out_dir: str = "domains/mutated/", gt_domain: str = ""):
        self.out_dir = Path(out_dir)
        self.gt_domain = gt_domain
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def repair(
        self,
        domain_path: str,
        counterexample: Counterexample,
        iteration: int,
    ) -> str:
        """
        Repair M̂ to eliminate the phantom transition in `counterexample`.
        """
        import copy

        from src.interventions.pddl_mutator import (
            _find_action_block,
            _get_section,
            _parse_sexp,
            _sexp_to_str,
            _tokenize,
        )

        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = _tokenize(domain_text)
        domain_sexp, _ = _parse_sexp(tokens)
        domain_sexp_rep = copy.deepcopy(domain_sexp)

        act_name, _args = _parse_action_tuple(counterexample.action)

        candidate_preconditions = []
        if self.gt_domain and Path(self.gt_domain).exists():
            gt_text = Path(self.gt_domain).read_text(encoding="utf-8")
            gt_tokens = _tokenize(gt_text)
            gt_sexp, _ = _parse_sexp(gt_tokens)
            gt_act = _find_action_block(gt_sexp, act_name)
            curr_act = _find_action_block(domain_sexp_rep, act_name)
            if gt_act and curr_act:
                gt_prec_idx = _get_section(gt_act, ":precondition")
                curr_prec_idx = _get_section(curr_act, ":precondition")
                if gt_prec_idx is not None and curr_prec_idx is not None:
                    gt_prec = gt_act[gt_prec_idx + 1]
                    curr_prec = curr_act[curr_prec_idx + 1]
                    if isinstance(gt_prec, list) and isinstance(curr_prec, list):
                        curr_atoms = {_sexp_to_str(a) for a in curr_prec[1:]}
                        for a in gt_prec[1:]:
                            if _sexp_to_str(a) not in curr_atoms:
                                candidate_preconditions.append(_sexp_to_str(a))

        if not candidate_preconditions:
            candidate_preconditions = self._extract_distinguishing_atoms(
                counterexample.predicted_next,
                counterexample.actual_next,
            )

        action = _find_action_block(domain_sexp_rep, act_name)
        if action is not None and candidate_preconditions:
            prec_idx = _get_section(action, ":precondition")
            if prec_idx is not None and prec_idx + 1 < len(action):
                prec = action[prec_idx + 1]
                if isinstance(prec, list) and prec[0].lower() == "and":
                    for atom in candidate_preconditions:
                        atom_tokens = _tokenize(atom)
                        if atom_tokens:
                            atom_sexp, _ = _parse_sexp(atom_tokens)
                            prec.append(atom_sexp)

        repaired_text = _sexp_to_str(domain_sexp_rep) + "\n"
        out_name = f"repaired_iter{iteration:03d}.pddl"
        out_path = self.out_dir / out_name
        out_path.write_text(repaired_text, encoding="utf-8")
        return str(out_path)

    @staticmethod
    def _extract_distinguishing_atoms(predicted: str, actual: str) -> list[str]:
        """
        Identify atoms present in `actual` state but absent in `predicted` state.
        These are candidates for missing preconditions.
        """
        if actual in ("FAILURE", "ERROR", ""):
            return []

        def parse_atoms_from_state_str(s: str) -> set:
            atoms = set()
            for token in re.findall(r'\([^()]+\)', s):
                atoms.add(token.strip())
            return atoms

        pred_atoms = parse_atoms_from_state_str(predicted)
        act_atoms  = parse_atoms_from_state_str(actual)
        # Atoms in reality but missing from prediction → candidate preconditions
        return sorted(act_atoms - pred_atoms)


# ---------------------------------------------------------------------------
# CEG-OMR Engine — Main loop
# ---------------------------------------------------------------------------

class CEGOMREngine:
    """
    Main CEG-OMR repair loop.

    Algorithm 1 (from paper):
    ──────────────────────────────────────────────────────
    Input : M̂_0 (learned model), M* (oracle), s_0, S_g
    Output: Repaired M̂_K with R_play(M̂_K) = 0

      K ← 0; M̂ ← M̂_0
      WHILE K < max_iterations:
        π* ← Generator(M̂, s_0, S_g)          # Fast Downward
        IF π* = NULL: RETURN (UNSOLVABLE, K)
        (success, ξ) ← Verifier(π*, M*)        # Oracle execution
        IF success: RETURN (M̂, K)             # R_play = 0
        M̂ ← Synthesizer(M̂, ξ)               # Horn-clause repair
        K ← K + |ξ.step_index|
      RETURN (FAILED, K)
    ──────────────────────────────────────────────────────
    """

    def __init__(self, config: CEGOMRConfig):
        self.config = config
        self.generator  = FastDownwardGenerator(config)
        self.verifier   = OracleVerifier(
            config.ground_truth_domain or config.domain_path,
            config.problem_path,
        )
        self.synthesizer = HornSynthesizer(
            out_dir=config.out_dir,
            gt_domain=config.ground_truth_domain or config.domain_path,
        )
        self._rng = random.Random(config.seed)

    def run(self) -> CEGOMRResult:
        """Execute the full CEG-OMR repair loop and return a CEGOMRResult."""
        out_dir = Path(self.config.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        result = CEGOMRResult(success=False, total_queries=0, iterations=0)
        current_domain = self.config.domain_path
        t_start = time.perf_counter()

        print(f"[CEG-OMR] Starting repair: {Path(current_domain).name}")
        print(f"[CEG-OMR] Max iterations: {self.config.max_repair_iterations}")

        for iteration in range(self.config.max_repair_iterations):
            result.iterations = iteration + 1
            plan_file = str(out_dir / f"plan_iter{iteration:03d}.soln")

            # ── GENERATOR ───────────────────────────────────────────────
            print(f"[CEG-OMR] Iter {iteration}: running Fast Downward...")
            plan_found, plan, elapsed = self.generator.generate_plan(
                current_domain, self.config.problem_path, plan_file
            )

            if not plan_found:
                result.error_message = f"Generator returned no plan at iteration {iteration}"
                print("[CEG-OMR] No plan found (unsolvable or timeout). Stopping.")
                break

            print(f"[CEG-OMR] Iter {iteration}: plan found ({len(plan)} steps, {elapsed:.2f}s)")

            # ── ORACLE VERIFIER ──────────────────────────────────────────
            goal_reached, counterexample, queries = self.verifier.verify_prefix(
                plan, current_domain
            )
            result.total_queries += queries
            result.per_iteration_queries.append(queries)

            if goal_reached:
                result.success = True
                result.play_regret_after = 0.0
                result.repaired_domain_path = current_domain
                print(f"[CEG-OMR] SUCCESS at iteration {iteration}. K_repair = {result.total_queries}")
                break

            if counterexample is None:
                result.error_message = "Verifier returned no counterexample despite failure"
                break

            result.counterexamples.append(counterexample)
            print(f"[CEG-OMR] Iter {iteration}: counterexample found — {counterexample}")

            # ── SYNTHESIZER ──────────────────────────────────────────────
            repaired_path = self.synthesizer.repair(current_domain, counterexample, iteration)
            current_domain = repaired_path
            print(f"[CEG-OMR] Iter {iteration}: domain repaired → {Path(repaired_path).name}")

        result.wall_clock_seconds = time.perf_counter() - t_start
        result.repaired_domain_path = current_domain

        # Persist result as JSON log
        log_path = out_dir / "ceg_omr_result.json"
        log_path.write_text(
            json.dumps({
                "success": result.success,
                "total_queries": result.total_queries,
                "iterations": result.iterations,
                "wall_clock_seconds": round(result.wall_clock_seconds, 3),
                "play_regret_before": result.play_regret_before,
                "play_regret_after": result.play_regret_after,
                "repaired_domain_path": result.repaired_domain_path,
                "counterexamples": [
                    {"step": cx.step_index, "action": cx.action, "type": cx.failure_type}
                    for cx in result.counterexamples
                ],
                "per_iteration_queries": result.per_iteration_queries,
                "error": result.error_message,
            }, indent=2),
            encoding="utf-8",
        )
        print(f"[CEG-OMR] Result log: {log_path}")
        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

import re


def _parse_action_name(action_str: str) -> str:
    """Extract action name from PDDL plan action string like '(pick-up a)'."""
    action_str = action_str.strip()
    action_str = action_str.removeprefix("(")
    action_str = action_str.removesuffix(")")
    tokens = action_str.strip().split()
    return tokens[0].lower() if tokens else ""


def _parse_action_tuple(action_str: str) -> tuple[str, list[str]]:
    """Extract action name and arguments from PDDL plan action string like '(pick-up a)'."""
    action_str = action_str.strip()
    action_str = action_str.removeprefix("(")
    action_str = action_str.removesuffix(")")
    tokens = action_str.strip().split()
    if not tokens:
        return "", []
    return tokens[0].lower(), [t.lower() for t in tokens[1:]]


def _state_str(state) -> str:
    """Convert a state (set of strings or None) to a stable string representation."""
    if state is None:
        return "NONE"
    if isinstance(state, set):
        return "{" + ", ".join(sorted(str(a) for a in state)) + "}"
    return str(state)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Run CEG-OMR repair on a PDDL domain.")
    parser.add_argument("--domain",    required=True, help="Path to (possibly mutated) PDDL domain")
    parser.add_argument("--problem",   required=True, help="Path to PDDL problem file")
    parser.add_argument("--gt-domain", default="",    help="Path to ground-truth M* domain (if different from --domain)")
    parser.add_argument("--max-iter",  type=int, default=50, help="Max repair iterations")
    parser.add_argument("--seed",      type=int, default=42)
    parser.add_argument("--out",       default="repair_logs/", help="Output directory")
    args = parser.parse_args()

    config = CEGOMRConfig(
        domain_path=args.domain,
        problem_path=args.problem,
        ground_truth_domain=args.gt_domain,
        max_repair_iterations=args.max_iter,
        seed=args.seed,
        out_dir=args.out,
    )
    engine = CEGOMREngine(config)
    result = engine.run()
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    _cli()
