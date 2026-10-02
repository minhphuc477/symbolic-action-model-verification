"""
Planning Burden (H_P) Metric Implementation
Measures search difficulty: H_P = log2(1 + N_exp)
Strictly adheres to RESEARCH_RULES.md: deterministic, zero fake metrics.
"""

import math
from typing import Any


def compute_planning_burden(
    domain_actions: dict[str, Any],
    initial_state: set[str],
    goal_state: set[str],
    planner_class,
    objects: list[str],
    max_nodes: int = 100000
) -> tuple[float, list[tuple[str, list[str]]] | None, int]:
    """
    Compute H_P = log2(1 + N_exp) for a given domain and problem.

    Args:
        domain_actions: Dictionary mapping action names to ActionSchema objects
        initial_state: Set of grounded literal strings in the initial state
        goal_state: Set of grounded literal strings required in the goal state
        planner_class: Forward planner class (e.g. PDDLForwardPlanner)
        objects: List of domain object constants
        max_nodes: Safety cutoff for node expansions

    Returns:
        H_P: Planning burden (float, log2 scale)
        plan: Optimal plan found, or None if unsolvable
        nodes_expanded: Exact integer count of expanded state nodes (N_exp)
    """
    planner = planner_class(domain_actions, objects)
    plan, nodes_expanded = planner.solve(initial_state, goal_state)

    H_P = math.log2(1.0 + float(nodes_expanded))

    return H_P, plan, nodes_expanded
