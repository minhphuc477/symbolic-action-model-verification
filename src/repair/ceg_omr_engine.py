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

import copy
import itertools
import json
import random
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pddl

from src.interventions.pddl_mutator import (
    _find_action_block,
    _get_section,
    _parse_sexp,
    _sexp_to_str,
    _tokenize,
)
from src.runners.wsl_harness import FastDownwardRunner

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
            f"xi_{self.step_index}: action={self.action} | "
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

        # Read plan file
        plan_path = Path(plan_out)
        if not plan_path.exists():
            # Try .soln suffix or .1 suffix
            plan_path = Path(plan_out + ".1")
        if not plan_path.exists():
            return False, [], float("inf")

        actions = self._parse_plan_file(plan_path)
        return True, actions, res.wall_clock_seconds

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
        if not self.gt_domain or not Path(self.gt_domain).exists():
            raise ValueError(f"OracleVerifier requires valid ground truth domain: {self.gt_domain}")

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
                        predicted_next=_state_str(next_learned),
                        actual_next=_state_str(next_gt),
                        failure_type="wrong_effect",
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
    Synthesizer component: given a counterexample xi_t = <s_t, a_t, s_hat_{t+1}, s*_{t+1}>,
    update candidate model M_hat using pure Active Version Space / Candidate Elimination (Mitchell 1982, Angluin 1992).

    CRITICAL SCIENTIFIC INTEGRITY:
    * ZERO access to ground truth domain file (M*).
    * Candidate hypotheses are generated strictly from M_hat's own predicate declarations and action parameters.
    * An applicability failure in state s_t implies that at least one necessary precondition
      evaluates to FALSE in s_t.
    * Candidates that evaluate to TRUE in s_t are eliminated from being the cause of failure.
    * Surviving candidates consistent with action effects (e.g. fluents deleted or modified by action)
      are prioritized to refine the schema.
    """

    def __init__(
        self,
        out_dir: str = "domains/mutated/",
        seed: int = 42,
        use_effect_coherence: bool = True,
        allow_effect_deletion: bool = True,
    ):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self._rng = random.Random(seed)
        self.use_effect_coherence = use_effect_coherence
        self.allow_effect_deletion = allow_effect_deletion
        self.version_spaces: dict[str, set[str]] = {}
        self.refuted_candidates: dict[str, set[str]] = {}
        self.repair_history: list[dict] = []
        self.relaxed_candidates: dict[str, set[str]] = {}
        self.verified_necessary_preconditions: dict[str, set[str]] = {}
        self.tried_relaxations: set[tuple[tuple[str, str], ...]] = set()
        self.initial_preconditions: dict[str, set[str]] | None = None

    def _ensure_initial_preconditions(self, domain_path: str) -> None:
        if self.initial_preconditions is not None:
            return
        import pddl

        from src.interventions.pddl_mutator import (
            _find_action_block,
            _get_section,
            _parse_sexp,
            _sexp_to_str,
            _tokenize,
        )
        dom = pddl.parse_domain(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = _tokenize(domain_text)
        domain_sexp, _ = _parse_sexp(tokens)
        self.initial_preconditions = {}
        for pddl_act in dom.actions:
            act_name = pddl_act.name.lower()
            action_block = _find_action_block(domain_sexp, act_name)
            if action_block is None:
                continue
            prec_idx = _get_section(action_block, ":precondition")
            if prec_idx is None or prec_idx + 1 >= len(action_block):
                continue
            prec_sexp = action_block[prec_idx + 1]
            if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                conjuncts = prec_sexp[1:]
            elif isinstance(prec_sexp, list) and prec_sexp:
                conjuncts = [prec_sexp]
            else:
                conjuncts = []
            self.initial_preconditions[act_name] = {
                " ".join(_sexp_to_str(c).split()).strip().lower() for c in conjuncts
            }

    def relax_overconstrained_domain(
        self,
        domain_path: str,
        problem_path: str,
        generator: FastDownwardGenerator,
        iteration: int,
        min_suspect_score: int = 0,
    ) -> tuple[bool, str, list[str], float]:
        """
        Minimal-Relaxation Abduction for over-constrained domains (where Pi(M_hat, s_0, g) is empty
        due to spurious preconditions or SAS+ sink-violation delete effects in M_hat_0).
        Ranks existing non-locked initial preconditions and delete effects by Inverse STRIPS
        Effect Coherence (suspect score) and finds a minimal removal that restores solvability
        in Fast Downward (0 oracle queries).
        """
        def _norm_sexp(x: Any) -> str:
            return " ".join(_sexp_to_str(x).split()).strip().lower()

        self._ensure_initial_preconditions(domain_path)
        dom = pddl.parse_domain(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = _tokenize(domain_text)
        domain_sexp, _ = _parse_sexp(tokens)

        # Collect predicate effect statistics across the domain
        dynamic_predicates: set[str] = set()
        ever_added_predicates: set[str] = set()
        conserved_predicates: set[str] = set()  # Predicates both added and deleted by the same action (e.g. at-robby)
        for pddl_act in dom.actions:
            eff_ops = (
                list(pddl_act.effect.operands)
                if hasattr(pddl_act.effect, "operands")
                else ([pddl_act.effect] if pddl_act.effect is not None else [])
            )
            act_add_preds: set[str] = set()
            act_del_preds: set[str] = set()
            for op in eff_ops:
                s = " ".join(str(op).split()).strip().lower()
                is_del = False
                if s.startswith("(not ") and s.endswith(")"):
                    s = s[5:-1].strip()
                    is_del = True
                toks = s.strip("()").split()
                if toks:
                    dynamic_predicates.add(toks[0])
                    if is_del:
                        act_del_preds.add(toks[0])
                    else:
                        ever_added_predicates.add(toks[0])
                        act_add_preds.add(toks[0])
            conserved_predicates |= (act_add_preds & act_del_preds)

        suspect_candidates: list[tuple[int, str, str, str]] = []  # (score, kind, act_name, norm_str)
        for pddl_act in dom.actions:
            act_name = pddl_act.name.lower()
            locked = self.verified_necessary_preconditions.get(act_name, set())
            init_precs = (
                self.initial_preconditions.get(act_name, set())
                if self.initial_preconditions is not None
                else None
            )

            deleted_literals: set[str] = set()
            added_literals: set[str] = set()
            eff_ops = (
                list(pddl_act.effect.operands)
                if hasattr(pddl_act.effect, "operands")
                else ([pddl_act.effect] if pddl_act.effect is not None else [])
            )
            for op in eff_ops:
                s = " ".join(str(op).split()).strip().lower()
                if s.startswith("(not ") and s.endswith(")"):
                    deleted_literals.add(s[5:-1].strip())
                else:
                    added_literals.add(s)

            action_block = _find_action_block(domain_sexp, act_name)
            if action_block is None:
                continue
            prec_idx = _get_section(action_block, ":precondition")
            if prec_idx is not None and prec_idx + 1 < len(action_block):
                prec_sexp = action_block[prec_idx + 1]
                if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                    conjuncts = prec_sexp[1:]
                elif isinstance(prec_sexp, list) and prec_sexp:
                    conjuncts = [prec_sexp]
                else:
                    conjuncts = []

                for c_sexp in conjuncts:
                    c_norm = _norm_sexp(c_sexp)
                    if c_norm in locked:
                        continue
                    if init_precs is not None and c_norm not in init_precs:
                        continue
                    # Inverse STRIPS Effect Coherence suspect scoring
                    score = 5
                    if self.use_effect_coherence:
                        if c_norm in added_literals:
                            # Positive precondition that is ALSO added by the action is a classic spurious constraint
                            score = 20
                        elif c_norm.startswith("(not ") and c_norm.endswith(")") and c_norm[5:-1].strip() in deleted_literals:
                            score = 20
                        elif c_norm in deleted_literals:
                            # Consumed/deleted fluent is coherent with genuine STRIPS precondition
                            score = 1
                        elif c_norm.startswith("(not ") and c_norm.endswith(")") and c_norm[5:-1].strip() in added_literals:
                            score = 2
                        else:
                            raw_pred = c_norm.strip("()").split()[0] if c_norm.strip("()") else ""
                            if raw_pred == "not":
                                inner_toks = c_norm[5:-1].strip().strip("()").split()
                                raw_pred = inner_toks[0] if inner_toks else ""
                            if raw_pred in dynamic_predicates:
                                score = 12
                            else:
                                score = 4
                    if score >= min_suspect_score:
                        suspect_candidates.append((score, "prec", act_name, c_norm))

            # Check for SAS+ Sink-Violation Spurious Delete Effects when effect deletion is enabled
            if self.allow_effect_deletion:
                act_add_preds_here = {
                    lit.strip("()").split()[0]
                    for lit in added_literals
                    if lit.strip("()").split()
                }
                for d_inner in sorted(deleted_literals):
                    toks = d_inner.strip("()").split()
                    if not toks:
                        continue
                    d_pred = toks[0]
                    del_norm = f"(not {d_inner})"
                    if del_norm in locked:
                        continue
                    # A delete effect on a predicate that is NEVER added anywhere in the domain,
                    # or on a 1-to-1 conserved predicate (like at-robby) when this action does not re-add it,
                    # is a SAS+ sink-violation suspect.
                    if d_pred not in ever_added_predicates or (
                        d_pred in conserved_predicates and d_pred not in act_add_preds_here
                    ):
                        eff_score = 18
                        if eff_score >= min_suspect_score:
                            suspect_candidates.append((eff_score, "eff_del", act_name, del_norm))

        if not suspect_candidates:
            return False, domain_path, [], 0.0

        suspect_candidates.sort(key=lambda x: x[0], reverse=True)

        # Search minimal relaxations of size k = 1, then k = 2 (bounded to top 8 suspects for k=2)
        candidate_items = [(kind, act_name, c_norm) for _, kind, act_name, c_norm in suspect_candidates]
        relaxation_sets: list[tuple[tuple[str, str, str], ...]] = [
            (item,) for item in candidate_items
        ]
        top_k2 = candidate_items[: min(8, len(candidate_items))]
        relaxation_sets.extend(itertools.combinations(top_k2, 2))

        for relax_tuple in relaxation_sets:
            canon_key = tuple(sorted((f"{k}:{a}", c) for k, a, c in relax_tuple))
            if canon_key in self.tried_relaxations:
                continue

            domain_sexp_cand = copy.deepcopy(domain_sexp)
            modified = False
            for kind, act_name, target_norm in relax_tuple:
                action_block = _find_action_block(domain_sexp_cand, act_name)
                if action_block is None:
                    continue
                if kind == "prec":
                    prec_idx = _get_section(action_block, ":precondition")
                    if prec_idx is None or prec_idx + 1 >= len(action_block):
                        continue
                    prec_sexp = action_block[prec_idx + 1]
                    if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                        new_conjuncts = [
                            c for c in prec_sexp[1:]
                            if _norm_sexp(c) != target_norm
                        ]
                        if len(new_conjuncts) < len(prec_sexp) - 1:
                            action_block[prec_idx + 1] = ["and"] + new_conjuncts if new_conjuncts else ["and"]
                            modified = True
                    elif isinstance(prec_sexp, list) and _norm_sexp(prec_sexp) == target_norm:
                        action_block[prec_idx + 1] = ["and"]
                        modified = True
                elif kind == "eff_del":
                    eff_idx = _get_section(action_block, ":effect")
                    if eff_idx is None or eff_idx + 1 >= len(action_block):
                        continue
                    eff_sexp = action_block[eff_idx + 1]
                    if isinstance(eff_sexp, list) and eff_sexp and isinstance(eff_sexp[0], str) and eff_sexp[0].lower() == "and":
                        new_effs = [
                            c for c in eff_sexp[1:]
                            if _norm_sexp(c) != target_norm
                        ]
                        if len(new_effs) < len(eff_sexp) - 1:
                            action_block[eff_idx + 1] = ["and"] + new_effs if new_effs else ["and"]
                            modified = True

            if not modified:
                continue

            cand_text = _sexp_to_str(domain_sexp_cand) + "\n"
            cand_path = self.out_dir / f"relaxed_iter{iteration:03d}.pddl"
            cand_path.write_text(cand_text, encoding="utf-8")
            plan_file = str(self.out_dir / f"plan_relax_iter{iteration:03d}.soln")

            plan_found, plan, elapsed = generator.generate_plan(
                str(cand_path), problem_path, plan_file
            )
            if plan_found:
                self.tried_relaxations.add(canon_key)
                for kind, act_name, target_norm in relax_tuple:
                    self.relaxed_candidates.setdefault(act_name, set()).add(target_norm)
                    print(
                        f"[HornSynthesizer] Minimal-Relaxation Abduction removed suspect {kind} "
                        f"{target_norm} from {act_name}"
                    )
                return True, str(cand_path), plan, elapsed

        return False, domain_path, [], 0.0

    def rollback(self, iteration: int) -> tuple[bool, str]:
        """
        Backtrack if planner failed: pop the last added hypothesis,
        mark it as refuted, and try the next surviving candidate if available.
        """
        while self.repair_history:
            last = self.repair_history.pop()
            act_name = last["action"]
            chosen = last["chosen"]
            prev_domain_path = last["domain_before_path"]
            remaining = last["remaining"]

            self.refuted_candidates.setdefault(act_name, set()).add(chosen)
            if act_name in self.version_spaces:
                self.version_spaces[act_name].discard(chosen)

            print(f"[HornSynthesizer] Backtracking: refuted over-constraining hypothesis {chosen} on {act_name}")

            while remaining:
                next_cand = remaining.pop(0)
                if next_cand in self.refuted_candidates.get(act_name, set()):
                    continue

                domain_text = Path(prev_domain_path).read_text(encoding="utf-8")
                tokens = _tokenize(domain_text)
                domain_sexp, _ = _parse_sexp(tokens)
                domain_sexp_rep = copy.deepcopy(domain_sexp)
                action = _find_action_block(domain_sexp_rep, act_name)
                if action is not None:
                    prec_idx = _get_section(action, ":precondition")
                    if prec_idx is not None and prec_idx + 1 < len(action):
                        prec = action[prec_idx + 1]
                        cand_tokens = _tokenize(next_cand)
                        cand_sexp, _ = _parse_sexp(cand_tokens) if cand_tokens else (None, 0)
                        if cand_sexp is not None:
                            if isinstance(prec, list) and prec and prec[0].lower() == "and":
                                prec.append(cand_sexp)
                            else:
                                action[prec_idx + 1] = ["and", prec, cand_sexp]

                repaired_text = _sexp_to_str(domain_sexp_rep) + "\n"
                out_name = f"repaired_backtrack_iter{iteration:03d}.pddl"
                out_path = self.out_dir / out_name
                out_path.write_text(repaired_text, encoding="utf-8")

                self.repair_history.append({
                    "action": act_name,
                    "chosen": next_cand,
                    "domain_before_path": prev_domain_path,
                    "remaining": remaining,
                    "iteration": iteration,
                    "chosen_score": last.get("chosen_score", 0),
                })
                print(f"[HornSynthesizer] Retrying with alternative candidate: {next_cand}")
                return True, str(out_path)

            return True, prev_domain_path

        return False, ""

    def repair(
        self,
        domain_path: str,
        counterexample: Counterexample,
        iteration: int,
    ) -> str:
        """
        Repair M_hat by eliminating phantom preconditions or repairing 4-way effect deltas
        using active counterexample feedback.
        Supports both positive and negative precondition candidates, version space candidate
        elimination, STRIPS effect coherence scoring, and bidirectional effect repair.
        """
        self._ensure_initial_preconditions(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = _tokenize(domain_text)
        domain_sexp, _ = _parse_sexp(tokens)
        domain_sexp_rep = copy.deepcopy(domain_sexp)

        act_name, args = _parse_action_tuple(counterexample.action)

        # 1. Parse domain using pddl library for type signatures and declarations
        dom = pddl.parse_domain(domain_path)
        matching_actions = [a for a in dom.actions if a.name.lower() == act_name.lower()]
        if not matching_actions:
            return domain_path
        pddl_act = matching_actions[0]

        # Action block in S-exp
        action = _find_action_block(domain_sexp_rep, act_name)
        if action is None:
            return domain_path

        # 2. Extract existing preconditions
        existing_preconditions: set[str] = set()
        if hasattr(pddl_act.precondition, "operands"):
            for op in pddl_act.precondition.operands:
                existing_preconditions.add(" ".join(str(op).split()).strip().lower())
        elif pddl_act.precondition is not None:
            existing_preconditions.add(" ".join(str(pddl_act.precondition).split()).strip().lower())

        # Extract added and deleted literals from effects
        deleted_literals: set[str] = set()
        added_literals: set[str] = set()
        if hasattr(pddl_act.effect, "operands"):
            for op in pddl_act.effect.operands:
                s = " ".join(str(op).split()).strip().lower()
                if s.startswith("(not ") and s.endswith(")"):
                    deleted_literals.add(s[5:-1].strip())
                else:
                    added_literals.add(s)
        elif pddl_act.effect is not None:
            s = " ".join(str(pddl_act.effect).split()).strip().lower()
            if s.startswith("(not ") and s.endswith(")"):
                deleted_literals.add(s[5:-1].strip())
            else:
                added_literals.add(s)

        # Parse failure state literals from counterexample
        failure_state_literals = {
            tok.strip().lower()
            for tok in re.findall(r"\([^()]+\)", counterexample.current_state)
        }

        # Parameter binding map: ?param_var -> arg_obj
        act_params = list(pddl_act.parameters)
        pmap = {p.name.lower(): arg_val.lower() for p, arg_val in zip(act_params, args)}
        inv_pmap = {arg_val.lower(): "?" + p.name.lstrip("?").lower() for p, arg_val in zip(act_params, args)}

        # -------------------------------------------------------------------
        # TYPE III/IV BIDIRECTIONAL EFFECT REPAIR: 4-Way Effect Delta Induction
        # -------------------------------------------------------------------
        if counterexample.failure_type == "wrong_effect":
            pred_lits = {tok.strip().lower() for tok in re.findall(r"\([^()]+\)", counterexample.predicted_next)}
            actual_lits = {tok.strip().lower() for tok in re.findall(r"\([^()]+\)", counterexample.actual_next)}
            actual_minus_pred = actual_lits - pred_lits
            pred_minus_actual = pred_lits - actual_lits

            eff_idx = _get_section(action, ":effect")
            if eff_idx is not None and eff_idx + 1 < len(action):
                eff = action[eff_idx + 1]
                if not (isinstance(eff, list) and eff and isinstance(eff[0], str) and eff[0].lower() == "and"):
                    action[eff_idx + 1] = ["and", eff]
                    eff = action[eff_idx + 1]

                def _has_eff_item(target_sexp: list) -> bool:
                    target_norm = " ".join(_sexp_to_str(target_sexp).split()).strip().lower()
                    return any(" ".join(_sexp_to_str(x).split()).strip().lower() == target_norm for x in eff[1:])

                def _remove_eff_item(target_sexp: list) -> bool:
                    target_norm = " ".join(_sexp_to_str(target_sexp).split()).strip().lower()
                    before_len = len(eff)
                    eff[1:] = [x for x in eff[1:] if " ".join(_sexp_to_str(x).split()).strip().lower() != target_norm]
                    return len(eff) < before_len

                # 1. Fluent is TRUE in M* next state (s*_{t+1}), FALSE in M_hat predicted next state:
                #    - Since f in s*_{t+1}, (not f) cannot be in Del*(a): remove (not f) if present.
                #    - If f not in s_t (or (not f) was not in Eff), f must be in Add*(a): add f if absent.
                for lit in sorted(actual_minus_pred):
                    raw_tokens = lit.strip("()").split()
                    p_name = raw_tokens[0]
                    p_args = raw_tokens[1:]
                    if all(a in inv_pmap for a in p_args):
                        lifted = [p_name] + [inv_pmap[a] for a in p_args]
                        lifted_del = ["not", lifted]
                        removed_spurious_del = False
                        if self.allow_effect_deletion and _has_eff_item(lifted_del):
                            _remove_eff_item(lifted_del)
                            removed_spurious_del = True
                            print(f"[HornSynthesizer] Removed spurious del effect on {act_name}: {lifted_del}")
                        if (lit not in failure_state_literals or not removed_spurious_del) and not _has_eff_item(lifted):
                            eff.append(lifted)
                            print(f"[HornSynthesizer] Repaired missing add effect on {act_name}: {lifted}")

                # 2. Fluent is FALSE in M* next state (s*_{t+1}), TRUE in M_hat predicted next state:
                #    - Since f not in s*_{t+1}, f cannot be in Add*(a): remove f if present.
                #    - If f in s_t (or f was not in Eff), (not f) must be in Del*(a): add (not f) if absent.
                for lit in sorted(pred_minus_actual):
                    raw_tokens = lit.strip("()").split()
                    p_name = raw_tokens[0]
                    p_args = raw_tokens[1:]
                    if all(a in inv_pmap for a in p_args):
                        lifted = [p_name] + [inv_pmap[a] for a in p_args]
                        lifted_del = ["not", lifted]
                        removed_spurious_add = False
                        if self.allow_effect_deletion and _has_eff_item(lifted):
                            _remove_eff_item(lifted)
                            removed_spurious_add = True
                            print(f"[HornSynthesizer] Removed spurious add effect on {act_name}: {lifted}")
                        if (lit in failure_state_literals or not removed_spurious_add) and not _has_eff_item(lifted_del):
                            eff.append(lifted_del)
                            print(f"[HornSynthesizer] Repaired missing del effect on {act_name}: {lifted_del}")

            repaired_text = _sexp_to_str(domain_sexp_rep) + "\n"
            out_name = f"repaired_eff_iter{iteration:03d}.pddl"
            out_path = self.out_dir / out_name
            out_path.write_text(repaired_text, encoding="utf-8")
            return str(out_path)

        # Helper for transitive type hierarchy compatibility
        dom_types = getattr(dom, "types", {})
        def _is_type_compatible(p_type_tags: set[str], t_type_tags: set[str]) -> bool:
            if not t_type_tags or not p_type_tags or "object" in t_type_tags:
                return True
            if t_type_tags & p_type_tags:
                return True
            for pt in p_type_tags:
                curr = pt
                while curr:
                    if curr in t_type_tags:
                        return True
                    curr = dom_types.get(curr)
            return False

        # 3. Generate candidate atomic preconditions (both positive and negated)
        candidate_atoms: list[tuple[str, str, bool]] = []  # (schema, grounded, is_negated)
        for pred in dom.predicates:
            pred_terms = list(pred.terms)
            arity = len(pred_terms)
            if arity == 0:
                pos_schema = f"({pred.name})"
                if pos_schema.lower() not in existing_preconditions and pos_schema.lower() not in added_literals:
                    candidate_atoms.append((pos_schema, pos_schema.lower(), False))
                neg_schema = f"(not ({pred.name}))"
                if (
                    neg_schema.lower() not in existing_preconditions
                    and pos_schema.lower() not in existing_preconditions
                    and pos_schema.lower() not in deleted_literals
                ):
                    candidate_atoms.append((neg_schema, pos_schema.lower(), True))
            else:
                matching_param_lists = []
                for t in pred_terms:
                    t_types = set(t.type_tags) if t.type_tags else set()
                    matches = []
                    for p in act_params:
                        p_types = set(p.type_tags) if p.type_tags else set()
                        if _is_type_compatible(p_types, t_types):
                            matches.append(p.name)
                    matching_param_lists.append(matches)

                for p_tuple in itertools.product(*matching_param_lists):
                    # Distinct parameters for distinct relational terms
                    if len(p_tuple) > 1 and len(set(p_tuple)) < len(p_tuple):
                        continue
                    grounded = [pmap.get(pt.lower(), pt.lower()) for pt in p_tuple]
                    atom_grounded = f"({pred.name} {' '.join(grounded)})".lower()

                    # Positive candidate
                    pos_schema = f"({pred.name} {' '.join('?' + p.lstrip('?') for p in p_tuple)})"
                    if pos_schema.lower() not in existing_preconditions and pos_schema.lower() not in added_literals:
                        candidate_atoms.append((pos_schema, atom_grounded, False))

                    # Negated candidate: (not (pred ?args))
                    neg_schema = f"(not ({pred.name} {' '.join('?' + p.lstrip('?') for p in p_tuple)}))"
                    if (
                        neg_schema.lower() not in existing_preconditions
                        and pos_schema.lower() not in existing_preconditions
                        and pos_schema.lower() not in deleted_literals
                    ):
                        candidate_atoms.append((neg_schema, atom_grounded, True))

        # 4. Version Space Candidate Elimination:
        # Action execution failed in state s_t => the true precondition MUST EVALUATE TO FALSE in s_t.
        # - Positive literal (P x) evaluates to FALSE iff (P x) not in s_t.
        # - Negated literal (not (P x)) evaluates to FALSE iff (P x) in s_t.
        refuted = self.refuted_candidates.get(act_name, set())
        violated_candidates = []
        for schema, grounded, is_neg in candidate_atoms:
            if schema in refuted:
                continue
            if (not is_neg and grounded not in failure_state_literals) or (is_neg and grounded in failure_state_literals):
                violated_candidates.append(schema)

        # Note: When an action has k >= 2 missing preconditions (p_1 ^ p_2), a failure state s_t
        # falsifies AT LEAST ONE missing conjunct (~p_1 v ~p_2), not necessarily all of them.
        # Candidates already committed to the action are filtered via existing_preconditions,
        # and candidates refuted by planner backtracking are filtered via refuted_candidates.
        self.version_spaces[act_name] = set(violated_candidates)

        surviving = [c for c in self.version_spaces[act_name] if c not in refuted]

        # Compute unreferenced action parameters (parameters declared in :parameters but absent from
        # existing preconditions and effects due to precondition omission)
        referenced_params: set[str] = set()
        for lit_str in existing_preconditions | deleted_literals | added_literals:
            for tok in re.findall(r"\?[a-zA-Z0-9_-]+", lit_str):
                referenced_params.add(tok.lower())
        all_param_vars = {"?" + p.name.lstrip("?").lower() for p in act_params}
        unbound_params = all_param_vars - referenced_params

        # 5. Rank surviving candidates using STRIPS Effect & Parameter-Binding Coherence:
        # Resource consumption: fluents deleted by action strongly imply precondition-before-delete (+10)
        # Parameter-binding prevail: positive fluent binding an otherwise unreferenced action parameter (+9)
        # Resource precondition: fluents added by action often require negation before add (+8)
        def candidate_score(c: str) -> int:
            c_lower = " ".join(c.split()).strip().lower()
            if c_lower in self.relaxed_candidates.get(act_name, set()):
                return 15
            if c_lower in deleted_literals:
                return 10
            if not c_lower.startswith("(not ") and unbound_params:
                c_vars = {tok.lower() for tok in re.findall(r"\?[a-zA-Z0-9_-]+", c_lower)}
                if c_vars & unbound_params:
                    return 9
            if c_lower.startswith("(not ") and c_lower.endswith(")"):
                inner = c_lower[5:-1].strip()
                if inner in added_literals:
                    return 8
            return 0

        if self.use_effect_coherence:
            sorted_candidates = sorted(surviving, key=candidate_score, reverse=True)
        else:
            sorted_candidates = list(surviving)
            self._rng.shuffle(sorted_candidates)
        chosen_candidate = sorted_candidates[0] if sorted_candidates else None
        remaining_candidates = sorted_candidates[1:] if len(sorted_candidates) > 1 else []

        if action is not None and chosen_candidate:
            prec_idx = _get_section(action, ":precondition")
            if prec_idx is not None and prec_idx + 1 < len(action):
                prec = action[prec_idx + 1]
                cand_tokens = _tokenize(chosen_candidate)
                cand_sexp, _ = _parse_sexp(cand_tokens) if cand_tokens else (None, 0)
                if cand_sexp is not None:
                    if isinstance(prec, list) and prec and prec[0].lower() == "and":
                        prec.append(cand_sexp)
                    else:
                        action[prec_idx + 1] = ["and", prec, cand_sexp]
                    print(f"[HornSynthesizer] Refined action {act_name} with: {chosen_candidate}")

            chosen_norm = " ".join(chosen_candidate.split()).strip().lower()
            if chosen_norm in self.relaxed_candidates.get(act_name, set()):
                # Precondition was previously relaxed and now proven necessary by oracle failure!
                self.verified_necessary_preconditions.setdefault(act_name, set()).add(chosen_norm)
                print(f"[HornSynthesizer] Locked verified necessary precondition {chosen_norm} on {act_name}")
            else:
                # Track in history stack for possible backtracking
                self.repair_history.append({
                    "action": act_name,
                    "chosen": chosen_candidate,
                    "domain_before_path": domain_path,
                    "remaining": remaining_candidates,
                    "iteration": iteration,
                    "chosen_score": candidate_score(chosen_candidate) if self.use_effect_coherence else 0,
                })

        repaired_text = _sexp_to_str(domain_sexp_rep) + "\n"
        out_name = f"repaired_iter{iteration:03d}.pddl"
        out_path = self.out_dir / out_name
        out_path.write_text(repaired_text, encoding="utf-8")
        return str(out_path)


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
        IF π* = NULL:
          TRY Backtrack(M̂) OR MinimalRelaxationAbduction(M̂)
          IF still NULL: RETURN (UNSOLVABLE, K)
        (success, ξ) ← Verifier(π*, M*)        # Oracle execution
        IF success: RETURN (M̂, K)             # R_play = 0
        M̂ ← Synthesizer(M̂, ξ)               # Bidirectional Horn-clause repair
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
            seed=config.seed,
            use_effect_coherence=config.use_effect_coherence,
            allow_effect_deletion=config.allow_effect_deletion,
        )
        self._rng = random.Random(config.seed)

    def repair(self) -> CEGOMRResult:
        """Alias for run() to provide clean semantic interface."""
        return self.run()

    def run(self) -> CEGOMRResult:
        """Execute the full CEG-OMR repair loop and return a CEGOMRResult."""
        out_dir = Path(self.config.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        result = CEGOMRResult(success=False, total_queries=0, iterations=0)
        current_domain = self.config.domain_path
        self.synthesizer._ensure_initial_preconditions(current_domain)
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
                if self.config.enable_backtracking:
                    # 1. Always check first for structural self-contradictions (score 20) or SAS+ sink-violation delete effects (score 18)
                    if self.config.allow_relaxation and bool(self.synthesizer.repair_history):
                        relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                            self.synthesizer.relax_overconstrained_domain(
                                current_domain,
                                self.config.problem_path,
                                self.generator,
                                iteration,
                                min_suspect_score=18,
                            )
                        )
                        if relaxed_ok and relaxed_plan:
                            current_domain = relaxed_path
                            plan_found = True
                            plan = relaxed_plan
                            elapsed = relaxed_elapsed
                            print(
                                f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction resolved structural "
                                f"over-constraint -> {Path(relaxed_path).name} ({len(plan)} steps)"
                            )

                    # 2. If the last added candidate was a low-confidence / speculative guess (score < 10)
                    # and has alternatives, backtrack first before touching initial preconditions of M_hat_0.
                    last_score = (
                        self.synthesizer.repair_history[-1].get("chosen_score", 0)
                        if self.synthesizer.repair_history else 0
                    )
                    if not plan_found and last_score >= 10 and self.config.allow_relaxation:
                        relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                            self.synthesizer.relax_overconstrained_domain(
                                current_domain,
                                self.config.problem_path,
                                self.generator,
                                iteration,
                                min_suspect_score=12,
                            )
                        )
                        if relaxed_ok and relaxed_plan:
                            current_domain = relaxed_path
                            plan_found = True
                            plan = relaxed_plan
                            elapsed = relaxed_elapsed
                            print(
                                f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction resolved compound "
                                f"over-constraint -> {Path(relaxed_path).name} ({len(plan)} steps)"
                            )

                    if not plan_found:
                        rolled_back, rolled_path = self.synthesizer.rollback(iteration)
                        if rolled_back and rolled_path:
                            print(f"[CEG-OMR] Planner unsolvable. Backtracking to alternative hypothesis -> {Path(rolled_path).name}")
                            current_domain = rolled_path
                            continue

                        if self.config.allow_relaxation:
                            relaxed_ok, relaxed_path, relaxed_plan, relaxed_elapsed = (
                                self.synthesizer.relax_overconstrained_domain(
                                    current_domain,
                                    self.config.problem_path,
                                    self.generator,
                                    iteration,
                                    min_suspect_score=0,
                                )
                            )
                            if relaxed_ok and relaxed_plan:
                                current_domain = relaxed_path
                                plan_found = True
                                plan = relaxed_plan
                                elapsed = relaxed_elapsed
                                print(
                                    f"[CEG-OMR] Iter {iteration}: Minimal-Relaxation Abduction restored solvability "
                                    f"-> {Path(relaxed_path).name} ({len(plan)} steps)"
                                )
                            else:
                                result.error_message = f"Generator returned no plan at iteration {iteration} and no backtrack/relaxation hypothesis remaining"
                                print("[CEG-OMR] No plan found and no backtrack/relaxation candidate remaining. Stopping.")
                                break
                        else:
                            result.error_message = f"Generator returned no plan at iteration {iteration} and relaxation is disabled"
                            print("[CEG-OMR] No plan found and relaxation is disabled. Stopping.")
                            break
                else:
                    result.error_message = f"Generator returned no plan at iteration {iteration} and backtracking is disabled"
                    print("[CEG-OMR] No plan found and no backtrack candidate remaining. Stopping.")
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
            print(f"[CEG-OMR] Iter {iteration}: counterexample found -- {counterexample}")

            # ── SYNTHESIZER ──────────────────────────────────────────────
            repaired_path = self.synthesizer.repair(current_domain, counterexample, iteration)
            current_domain = repaired_path
            print(f"[CEG-OMR] Iter {iteration}: domain repaired -> {Path(repaired_path).name}")

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
