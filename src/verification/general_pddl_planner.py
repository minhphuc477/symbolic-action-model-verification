"""
General Forward State-Space Search Planner & Ground-Truth Validator
Supports arbitrary STRIPS action schemas with n-ary parameters across IPC domains.
Strictly adheres to RESEARCH_RULES.md: deterministic, zero fake metrics.
"""

import collections
import itertools
from typing import Dict, List, Set, Tuple, Optional, Any
from src.metrics.transition_accuracy import ActionSchema, safe_ground

class GeneralForwardPlanner:
    def __init__(self, actions: Dict[str, ActionSchema], objects: List[str]):
        self.actions = actions
        self.objects = objects

    def get_ground_actions(self) -> List[Tuple[str, List[str]]]:
        grounded = []
        for name, schema in self.actions.items():
            k = len(schema.params)
            if k == 0:
                grounded.append((name, []))
            elif k == 1:
                for obj in self.objects:
                    grounded.append((name, [obj]))
            else:
                for args in itertools.product(self.objects, repeat=k):
                    grounded.append((name, list(args)))
        return grounded

    def solve(self, init_state: Set[str], goal_literals: Set[str], max_nodes: int = 50000) -> Tuple[Optional[List[Tuple[str, List[str]]]], int]:
        """Runs forward breadth-first search on candidate model M to find the shortest plan."""
        queue = collections.deque([(frozenset(init_state), [])])
        visited = {frozenset(init_state)}
        ground_actions = self.get_ground_actions()
        nodes_explored = 0

        while queue and nodes_explored < max_nodes:
            cur_frozen, path = queue.popleft()
            nodes_explored += 1
            cur_set = set(cur_frozen)

            if goal_literals.issubset(cur_set):
                return path, nodes_explored

            for act_name, args in ground_actions:
                schema = self.actions[act_name]
                pmap = {p: a for p, a in zip(schema.params, args)}
                if schema.is_applicable(cur_set, pmap):
                    next_set = schema.apply(cur_set, pmap)
                    if next_set is not None:
                        next_frozen = frozenset(next_set)
                        if next_frozen not in visited:
                            visited.add(next_frozen)
                            queue.append((next_frozen, path + [(act_name, args)]))

        return None, nodes_explored

    def execute_plan(self, init_state: Set[str], plan: List[Tuple[str, List[str]]],
                     gt_actions: Dict[str, ActionSchema], goal_literals: Set[str]) -> Tuple[bool, int, Optional[str]]:
        """
        Executes plan step-by-step strictly against Ground Truth domain M*.
        Returns (success, steps_completed, failure_reason).
        """
        cur_state = set(init_state)
        for i, (act_name, args) in enumerate(plan):
            if act_name not in gt_actions:
                return False, i, f"Action '{act_name}' does not exist in Ground Truth."
            gt_schema = gt_actions[act_name]
            pmap = {p: a for p, a in zip(gt_schema.params, args)}

            # Check applicability in true physics M*
            if not gt_schema.is_applicable(cur_state, pmap):
                violated = []
                for pre in gt_schema.preconditions:
                    gp = safe_ground(pre, pmap)
                    if gp.startswith('(not ') and gp.endswith(')'):
                        pos = gp[5:-1].strip()
                        if pos in cur_state:
                            violated.append(gp)
                    else:
                        if gp not in cur_state:
                            violated.append(gp)
                return False, i, f"Precondition violation at step {i+1} ({act_name} {' '.join(args)}): missing {violated}"

            # Apply true physics
            cur_state = gt_schema.apply(cur_state, pmap)

        reached = goal_literals.issubset(cur_state)
        if reached:
            return True, len(plan), None
        else:
            return False, len(plan), "Plan executed but Goal conditions not satisfied in M*."
