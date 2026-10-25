"""
Oracle Verifier Component for CEG-OMR
=====================================
Executes candidate plans against the ground-truth environment/domain M*, detects
the exact divergence or failure step, and extracts counterexample tuples.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.repair.config import Counterexample
from src.utils.sexp import parse_action_tuple


def state_str(state: set[str] | None) -> str:
    """Convert a state (set of strings or None) to a stable sorted string representation."""
    if state is None:
        return "NONE"
    if isinstance(state, set):
        return "{" + ", ".join(sorted(str(a) for a in state)) + "}"
    return str(state)


class OracleVerifier:
    """
    Executes a plan prefix against M* (ground truth domain) and detects
    the first divergence point.

    For PDDL domains: uses a lightweight Python forward transition evaluator.
    For game engines: can be subclassed to delegate to the real game engine RPC/socket.
    """

    def __init__(self, ground_truth_domain: str, problem_path: str):
        self.gt_domain = ground_truth_domain
        self.problem_path = problem_path
        self._gt_domain_text = (
            Path(ground_truth_domain).read_text(encoding="utf-8")
            if ground_truth_domain and Path(ground_truth_domain).exists()
            else ""
        )

    def verify_prefix(
        self,
        plan: list[str],
        learned_domain: str,
    ) -> tuple[bool, Counterexample | None, int]:
        """
        Execute candidate plan actions step-by-step against ground truth M*.
        Returns (goal_reached, counterexample, queries_consumed).
        """
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
                act_name, args = parse_action_tuple(action_str)

                gt_schema = gt_actions.get(act_name)
                learned_schema = learned_actions.get(act_name)

                if not gt_schema or not learned_schema:
                    cx = Counterexample(
                        step_index=i,
                        action=action_str,
                        predicted_next=state_str(state_learned),
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
                        predicted_next=state_str(state_learned),
                        actual_next="FAILURE",
                        failure_type="inapplicable",
                        current_state=state_str(state_gt),
                    )
                    return False, cx, queries

                if next_gt != next_learned:
                    cx = Counterexample(
                        step_index=i,
                        action=action_str,
                        predicted_next=state_str(next_learned),
                        actual_next=state_str(next_gt),
                        failure_type="wrong_effect",
                        current_state=state_str(state_gt),
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


# Backward compatibility aliases
_state_str = state_str
