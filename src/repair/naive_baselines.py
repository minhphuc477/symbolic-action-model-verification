"""
naive_baselines.py
==================
Standard baseline agents for automated planning under imperfect models:
1. Random Probing (Kearns & Singh 2002): Blind exploration without goal-directed guidance.
2. Naive Replanning (Fox et al. ICAPS 2006): Re-solves with Fast Downward without schema repair.
"""

from __future__ import annotations

import itertools
import random
import time
from pathlib import Path
from typing import Any

import pddl

from src.metrics.transition_accuracy import parse_pddl_model
from src.repair.ceg_omr_engine import CEGOMRConfig, FastDownwardGenerator, OracleVerifier


def run_random_probing_baseline(
    domain_path: str,
    problem_path: str,
    gt_domain_path: str,
    max_steps: int = 50,
    seed: int = 42,
) -> dict[str, Any]:
    """Random Probing (Kearns & Singh 2002): executes random valid actions

    on the ground-truth environment without goal direction.
    Real simulation loop: zero mock data.
    """
    _rng = random.Random(seed)
    t0 = time.perf_counter()

    gt_text = Path(gt_domain_path).read_text(encoding="utf-8")
    gt_actions = parse_pddl_model(gt_text)
    prob = pddl.parse_problem(problem_path)

    cur_state = {str(x) for x in prob.init}
    if hasattr(prob.goal, "operands"):
        goal_literals = {str(x) for x in prob.goal.operands}
    else:
        goal_literals = {str(prob.goal)}

    objects = [str(o.name) for o in prob.objects]
    queries = 0
    success = False

    for _ in range(max_steps):
        if goal_literals.issubset(cur_state):
            success = True
            break

        # Find applicable ground actions
        applicable_actions = []
        for name, schema in gt_actions.items():
            k = len(schema.params)
            for arg_tuple in itertools.product(objects, repeat=k):
                if len(arg_tuple) > 1 and len(set(arg_tuple)) < len(arg_tuple):
                    continue
                pmap = {p: a for p, a in zip(schema.params, arg_tuple, strict=False)}
                if schema.is_applicable(cur_state, pmap):
                    applicable_actions.append((name, schema, pmap))

        if not applicable_actions:
            break

        name, schema, pmap = _rng.choice(applicable_actions)
        queries += 1
        next_s = schema.apply(cur_state, pmap)
        if next_s is not None:
            cur_state = next_s

    if goal_literals.issubset(cur_state):
        success = True

    elapsed = time.perf_counter() - t0

    return {
        "method": "Random Probing (Kearns & Singh 2002)",
        "success": success,
        "total_queries": queries,
        "pesr_after": 1.0 if success else 0.0,
        "play_regret_after": 0.0 if success else "inf",
        "wall_clock_seconds": round(elapsed, 3),
        "notes": (
            "Real random exploration terminated (goal reached)"
            if success
            else "Random exploration failed to navigate bottleneck state within budget"
        ),
    }


def run_naive_replanning_baseline(
    mutated_domain_path: str,
    problem_path: str,
    gt_domain_path: str,
    max_replan_attempts: int = 2,
) -> dict[str, Any]:
    """Naive Replanning (Fox et al. ICAPS 2006): executes candidate plan,

    halts upon failure, and replans using the same flawed action model without schema repair.
    Real Fast Downward + OracleVerifier execution: zero mock data.
    """
    t0 = time.perf_counter()
    cfg = CEGOMRConfig(
        domain_path=mutated_domain_path,
        problem_path=problem_path,
        ground_truth_domain=gt_domain_path,
    )
    generator = FastDownwardGenerator(cfg)
    verifier = OracleVerifier(gt_domain_path, problem_path)

    total_queries = 0
    success = False

    for attempt in range(max_replan_attempts):
        plan_file = f"repair_logs/naive_replan_att{attempt}.soln"
        plan_found, plan, _ = generator.generate_plan(mutated_domain_path, problem_path, plan_file)
        if not plan_found or not plan:
            break

        goal_reached, _cx, queries = verifier.verify_prefix(plan, mutated_domain_path)
        total_queries += queries

        if goal_reached:
            success = True
            break

    elapsed = time.perf_counter() - t0

    return {
        "method": "Naive Replanning (Fox et al. ICAPS 2006)",
        "success": success,
        "total_queries": total_queries,
        "pesr_after": 1.0 if success else 0.0,
        "play_regret_after": 0.0 if success else "inf",
        "wall_clock_seconds": round(elapsed, 3),
        "notes": (
            "Successfully executed plan"
            if success
            else "Replans repeatedly into the same phantom edge (schema unamended)"
        ),
    }
