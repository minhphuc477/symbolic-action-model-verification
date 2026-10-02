"""
Learning Burden (B) Metric Implementation
Measures sample complexity required to achieve planning adequacy:
B_{L,D,P,epsilon}(G, x) = min { n in N : E_{T ~ D^n}[ Regret_P(L(T); G, x) ] <= epsilon }
Strictly adheres to RESEARCH_RULES.md: deterministic, zero fake metrics.
"""

import math
from collections.abc import Callable
from typing import Any

import numpy as np


def compute_play_regret(
    learned_domain: dict[str, Any],
    gt_domain: dict[str, Any],
    problem: dict[str, Any],
    planner_class
) -> float:
    """
    Compute R_play = cost(learned_plan) - cost(optimal_plan).

    If learned_plan fails during execution on ground truth physics M*,
    or if no plan can be found, returns float('inf').
    """
    initial_state = problem["init"]
    goal_state = problem["goal"]
    objects = problem["objects"]

    # 1. Solve problem on the learned model M_hat
    learned_planner = planner_class(learned_domain, objects)
    plan_learned, _ = learned_planner.solve(initial_state, goal_state)

    if plan_learned is None:
        return float('inf')

    # 2. Execute learned plan step-by-step strictly on Ground Truth M*
    success, _steps, _fail_reason = learned_planner.execute_plan(
        initial_state, plan_learned, gt_domain, goal_state
    )

    if not success:
        return float('inf')

    # 3. Compute optimal cost on Ground Truth M*
    gt_planner = planner_class(gt_domain, objects)
    plan_optimal, _ = gt_planner.solve(initial_state, goal_state)
    optimal_cost = len(plan_optimal) if plan_optimal is not None else float('inf')

    learned_cost = len(plan_learned)
    regret = float(max(0, learned_cost - optimal_cost))
    return regret

def compute_learning_burden(
    learner: Any,
    domain: dict[str, Any],
    problem: dict[str, Any],
    trace_generator: Callable[[int, int], Any],
    planner_class: Any,
    epsilon: float = 0.1,
    n_values: list[int] | None = None,
    n_seeds: int = 5
) -> dict[str, Any]:
    """
    Compute B = min n such that E[Regret] <= epsilon.

    Returns:
        {
            'B': int or float('inf'),
            'regret_curve': {n: (mean_regret, std_regret)},
            'n_values': [...],
            'converged': bool
        }
    """
    if n_values is None:
        n_values = [10, 20, 50, 100, 200, 500]

    regret_curve = {}

    for n in n_values:
        regrets = []
        for seed in range(n_seeds):
            traces = trace_generator(n, seed)
            # learner.learn returns an action model schema dictionary
            model = learner.learn(traces)
            regret = compute_play_regret(model, domain, problem, planner_class)
            regrets.append(regret)

        # Handle infinite regrets properly
        finite_regrets = [r for r in regrets if not math.isinf(r)]
        if len(finite_regrets) < len(regrets):
            mean_regret = float('inf')
            std_regret = 0.0
        else:
            mean_regret = float(np.mean(regrets))
            std_regret = float(np.std(regrets))

        regret_curve[n] = (mean_regret, std_regret)

        if mean_regret <= epsilon:
            return {
                'B': n,
                'regret_curve': regret_curve,
                'n_values': n_values,
                'converged': True
            }

    return {
        'B': float('inf'),
        'regret_curve': regret_curve,
        'n_values': n_values,
        'converged': False
    }
