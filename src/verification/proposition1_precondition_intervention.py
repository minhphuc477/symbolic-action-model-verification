"""
proposition1_precondition_intervention.py
Empirical Verification of Proposition 1 (Phantom Path Divergence & Verified-vs-Correct Gap).

Theoretical Claim (Proposition 1):
When an action model M_hat omits a precondition p in an action schema:
1. It introduces phantom transitions (shortcuts) in the state-space transition graph.
2. If p is a topological bottleneck, forward planning in M_hat exploits the phantom shortcut,
   synthesizing an illusory plan pi_{M_hat}.
3. Executing pi_{M_hat} in the true environment M* causes immediate execution failure:
   Plan Execution Success Rate (PESR) = 0.0, Play Regret (R_play) = INFINITY.
4. Concurrently, passive transition prediction accuracy (A_pred) over non-bottleneck traces
   can remain arbitrarily high (e.g. >90%), proving the Verified-vs-Correct Gap.

Strictly adheres to RESEARCH_RULES.md:
- Real forward graph search (BFS / A*).
- Step-by-step real execution validation on Ground Truth M*.
- Real transition accuracy A_pred evaluated over 100 genuine trajectory transitions.
- ZERO mock data, ZERO hardcoded formulas.
"""

import os
import sys
import collections
import re
from typing import Dict, List, Set, Tuple, Optional, Any

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import (
    evaluate_transition_accuracy,
    ActionSchema,
    parse_pddl_model,
    safe_ground
)

class PDDLForwardPlanner:
    """Real forward state-space search planner and environment execution validator."""

    def __init__(self, actions: Dict[str, ActionSchema], objects: List[str]):
        self.actions = actions
        self.objects = objects

    def get_ground_actions(self) -> List[Tuple[str, List[str]]]:
        grounded = []
        for name, schema in self.actions.items():
            num_params = len(schema.params)
            if num_params == 1:
                for obj in self.objects:
                    grounded.append((name, [obj]))
            elif num_params == 2:
                for o1 in self.objects:
                    for o2 in self.objects:
                        if o1 != o2:
                            grounded.append((name, [o1, o2]))
        return grounded

    def solve(self, init_state: Set[str], goal_literals: Set[str]) -> Tuple[Optional[List[Tuple[str, List[str]]]], int]:
        """Runs forward breadth-first search to find shortest optimal plan."""
        queue = collections.deque([(frozenset(init_state), [])])
        visited = {frozenset(init_state)}
        ground_actions = self.get_ground_actions()
        nodes_explored = 0

        while queue:
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
        Executes a plan step-by-step strictly against Ground Truth domain M*.
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
                # Identify violated ground truth preconditions
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

        # Check goal attainment
        reached = goal_literals.issubset(cur_state)
        if reached:
            return True, len(plan), None
        else:
            return False, len(plan), "Plan finished but Goal conditions not satisfied in M*."

def run_precondition_intervention_suite() -> Dict[str, Any]:
    """
    Executes controlled precondition interventions to test Proposition 1.
    """
    # 1. Load Ground Truth Domain
    gt_file = "benchmark_outputs/ground_truth.pddl"
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_pddl = f.read()
    gt_models = parse_pddl_model(gt_pddl)

    # Standard Tower Inversion Task: 3 blocks (a, b, c)
    # Init: C on B, B on A, A on table, C clear, hand empty.
    objects = ["a", "b", "c"]
    init_state = {
        "(on c b)", "(on b a)", "(ontable a)",
        "(clear c)", "(handempty)"
    }
    # Goal: A on B, B on C, C on table.
    goal_state = {"(on a b)", "(on b c)"}

    with open("benchmark_outputs/fama_normalized.pddl", "r", encoding="utf-8") as f:
        fama_pddl = f.read()
    with open("benchmark_outputs/locm2_normalized.pddl", "r", encoding="utf-8") as f:
        locm2_pddl = f.read()

    # 2. Define Experimental Conditions
    interventions = {
        "Control (Ground Truth M*)": {
            "pddl": gt_pddl,
            "description": "All preconditions intact (baseline)"
        },
        "FAMA Learned Model": {
            "pddl": fama_pddl,
            "description": "FAMA omission of (handempty) in pick-up"
        },
        "LOCM2 Learned Model": {
            "pddl": locm2_pddl,
            "description": "LOCM2 omission of delete effects and precondition conflation"
        },


        "Intervention: Omit (clear ?o1) in unstack": {
            "pddl": gt_pddl.replace(
                "(:action unstack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (on ?o1 ?o2) (clear ?o1) (handempty))",
                "(:action unstack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (on ?o1 ?o2) (handempty))"
            ),
            "description": "Permits unstacking covered blocks (phantom shortcut)"
        },
        "Intervention: Omit (handempty) in unstack": {
            "pddl": gt_pddl.replace(
                "(:action unstack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (on ?o1 ?o2) (clear ?o1) (handempty))",
                "(:action unstack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (on ?o1 ?o2) (clear ?o1))"
            ),
            "description": "Permits unstacking while already holding a block"
        },
        "Intervention: Omit (clear ?o2) in stack": {
            "pddl": gt_pddl.replace(
                "(:action stack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (holding ?o1) (clear ?o2))",
                "(:action stack\n\t     :parameters (?o1 ?o2)\n\t     :precondition (and (holding ?o1))"
            ),
            "description": "Permits stacking on top of covered blocks"
        }
    }

    results = {}

    for name, config in interventions.items():
        pddl_text = config["pddl"]
        model = parse_pddl_model(pddl_text)
        planner = PDDLForwardPlanner(model, objects)

        # A* / BFS Search on learned/intervened model
        plan, nodes = planner.solve(init_state, goal_state)

        # Check for phantom transitions in the plan
        phantom_edges = 0
        if plan:
            sim_state = set(init_state)
            for act_name, args in plan:
                gt_schema = gt_models[act_name]
                pmap = {p: a for p, a in zip(gt_schema.params, args)}
                # If illegal in GT M*, this step is a phantom edge!
                if not gt_schema.is_applicable(sim_state, pmap):
                    phantom_edges += 1
                # Advance simulation using learned model
                lrn_schema = model[act_name]
                lrn_pmap = {p: a for p, a in zip(lrn_schema.params, args)}
                sim_state = lrn_schema.apply(sim_state, lrn_pmap)

        # Real Execution on Ground Truth M*
        if plan:
            success, steps, fail_reason = planner.execute_plan(init_state, plan, gt_models, goal_state)
            pesr = 1.0 if success else 0.0
            r_play = "0" if success else "INFINITY"
        else:
            success, steps, fail_reason = False, 0, "No plan found"
            pesr = 0.0
            r_play = "INFINITY"

        # Calculate genuine passive transition accuracy over 100 test transitions
        t_eval = evaluate_transition_accuracy(pddl_text)
        a_pred = t_eval["a_pred"]

        results[name] = {
            "description": config["description"],
            "plan_found": plan is not None,
            "plan_length": len(plan) if plan else 0,
            "nodes_explored": nodes,
            "phantom_edges": phantom_edges,
            "PESR": pesr,
            "R_play": r_play,
            "fail_reason": fail_reason,
            "A_pred": a_pred,
            "plan_str": " -> ".join([f"{a[0]}({','.join(a[1])})" for a in plan]) if plan else "None"
        }

    return results

def print_proposition1_report(results: Dict[str, Any]):
    print("\n" + "="*110)
    print("PROPOSITION 1 EMPIRICAL VERIFICATION REPORT: PRECONDITION INTERVENTIONS & PHANTOM COLLAPSE")
    print("="*110)
    fmt = "{:<42} | {:<8} | {:<7} | {:<10} | {:<8} | {:<10}"
    print(fmt.format("Condition", "A_pred", "PlanLen", "Phantom", "PESR", "R_play"))
    print("-" * 110)
    for name, r in results.items():
        print(fmt.format(
            name[:42],
            f"{r['A_pred']:.3f}",
            r['plan_length'],
            f"{r['phantom_edges']}/{r['plan_length']}",
            f"{r['PESR']:.1f}",
            r['R_play']
        ))
    print("="*110)

    print("\nDetailed Diagnostic Breakdown per Condition:")
    for name, r in results.items():
        print(f"\n--- {name} ---")
        print(f"  Description:    {r['description']}")
        print(f"  Plan Found:     {r['plan_str']}")
        print(f"  Nodes Explored: {r['nodes_explored']}")
        print(f"  Phantom Edges:  {r['phantom_edges']}")
        print(f"  Plan Execution: PESR={r['PESR']}, R_play={r['R_play']}")
        if r['fail_reason']:
            print(f"  Execution Halt: {r['fail_reason']}")

if __name__ == "__main__":
    res = run_precondition_intervention_suite()
    print_proposition1_report(res)
