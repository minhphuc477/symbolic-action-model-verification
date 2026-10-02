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

Exhaustive Phase 3 Suite:
- Systematically tests all 9 individual precondition omissions in Blocksworld.
- Evaluates across 3 diverse benchmark tasks (Tower Inversion, Disassembly to Table, Tower Reassembly).
- Measures:
  * Passive Transition Accuracy (A_pred) over 100 genuine test transitions
  * Plan existence and plan length
  * Number of phantom edges in plan
  * Step-by-step real execution validation on M* (PESR, R_play, exact failure reason)
- Evaluates real learned models: FAMA and LOCM2.
"""

import collections
import json
import os
import sys
from typing import Any

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import (
    ActionSchema,
    evaluate_transition_accuracy,
    parse_pddl_model,
    safe_ground,
)


class PDDLForwardPlanner:
    """Real forward state-space search planner and environment execution validator."""

    def __init__(self, actions: dict[str, ActionSchema], objects: list[str]):
        self.actions = actions
        self.objects = objects

    def get_ground_actions(self) -> list[tuple[str, list[str]]]:
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

    def solve(self, init_state: set[str], goal_literals: set[str]) -> tuple[list[tuple[str, list[str]]] | None, int]:
        """Runs forward breadth-first search on M_hat to find the shortest plan."""
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

    def execute_plan(self, init_state: set[str], plan: list[tuple[str, list[str]]],
                     gt_actions: dict[str, ActionSchema], goal_literals: set[str]) -> tuple[bool, int, str | None]:
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
            return False, len(plan), "Plan executed but Goal conditions not satisfied in M*."

def get_benchmark_tasks() -> dict[str, dict[str, Any]]:
    """Defines 3 canonical planning tasks in Blocksworld."""
    objects = ["a", "b", "c"]
    return {
        "Task 1: Tower Inversion": {
            "objects": objects,
            "init": {"(on c b)", "(on b a)", "(ontable a)", "(clear c)", "(handempty)"},
            "goal": {"(on a b)", "(on b c)"},
            "optimal_cost": 6
        },
        "Task 2: Disassembly to Table": {
            "objects": objects,
            "init": {"(on c b)", "(on b a)", "(ontable a)", "(clear c)", "(handempty)"},
            "goal": {"(ontable c)", "(ontable b)", "(ontable a)", "(handempty)"},
            "optimal_cost": 4
        },
        "Task 3: Reassembly from Table": {
            "objects": objects,
            "init": {"(ontable a)", "(ontable b)", "(ontable c)", "(clear a)", "(clear b)", "(clear c)", "(handempty)"},
            "goal": {"(on a b)", "(on b c)"},
            "optimal_cost": 4
        }
    }

def get_precondition_interventions(gt_pddl: str) -> dict[str, dict[str, str]]:
    """Defines all 9 single-precondition omissions plus learned models."""
    with open("benchmark_outputs/fama_normalized.pddl", "r", encoding="utf-8") as f:
        fama_pddl = f.read()
    with open("benchmark_outputs/locm2_normalized.pddl", "r", encoding="utf-8") as f:
        locm2_pddl = f.read()

    return {
        "Control (Ground Truth M*)": {
            "pddl": gt_pddl,
            "action": "none", "omitted": "none",
            "desc": "All preconditions intact (baseline)"
        },
        # 1. pick-up omissions
        "Omit (clear ?o1) in pick-up": {
            "pddl": gt_pddl.replace("(and (clear ?o1) (ontable ?o1) (handempty))", "(and (ontable ?o1) (handempty))"),
            "action": "pick-up", "omitted": "(clear ?o1)",
            "desc": "Permits picking up covered blocks directly from table"
        },
        "Omit (ontable ?o1) in pick-up": {
            "pddl": gt_pddl.replace("(and (clear ?o1) (ontable ?o1) (handempty))", "(and (clear ?o1) (handempty))"),
            "action": "pick-up", "omitted": "(ontable ?o1)",
            "desc": "Permits picking up blocks from the top of stacks without unstacking"
        },
        "Omit (handempty) in pick-up": {
            "pddl": gt_pddl.replace("(and (clear ?o1) (ontable ?o1) (handempty))", "(and (clear ?o1) (ontable ?o1))"),
            "action": "pick-up", "omitted": "(handempty)",
            "desc": "Permits picking up a block while already holding another"
        },
        # 2. put-down omissions
        "Omit (holding ?o1) in put-down": {
            "pddl": gt_pddl.replace("(and (holding ?o1))", "(and )"),
            "action": "put-down", "omitted": "(holding ?o1)",
            "desc": "Permits putting down blocks out of thin air"
        },
        # 3. stack omissions
        "Omit (holding ?o1) in stack": {
            "pddl": gt_pddl.replace("(and (holding ?o1) (clear ?o2))", "(and (clear ?o2))"),
            "action": "stack", "omitted": "(holding ?o1)",
            "desc": "Permits stacking a block without holding it"
        },
        "Omit (clear ?o2) in stack": {
            "pddl": gt_pddl.replace("(and (holding ?o1) (clear ?o2))", "(and (holding ?o1))"),
            "action": "stack", "omitted": "(clear ?o2)",
            "desc": "Permits stacking onto already covered blocks"
        },
        # 4. unstack omissions
        "Omit (on ?o1 ?o2) in unstack": {
            "pddl": gt_pddl.replace("(and (on ?o1 ?o2) (clear ?o1) (handempty))", "(and (clear ?o1) (handempty))"),
            "action": "unstack", "omitted": "(on ?o1 ?o2)",
            "desc": "Permits unstacking blocks that are on table"
        },
        "Omit (clear ?o1) in unstack": {
            "pddl": gt_pddl.replace("(and (on ?o1 ?o2) (clear ?o1) (handempty))", "(and (on ?o1 ?o2) (handempty))"),
            "action": "unstack", "omitted": "(clear ?o1)",
            "desc": "Permits unstacking covered blocks from inside a tower"
        },
        "Omit (handempty) in unstack": {
            "pddl": gt_pddl.replace("(and (on ?o1 ?o2) (clear ?o1) (handempty))", "(and (on ?o1 ?o2) (clear ?o1))"),
            "action": "unstack", "omitted": "(handempty)",
            "desc": "Permits unstacking while already holding a block"
        },
        # Real Learned Models
        "FAMA Learned Model": {
            "pddl": fama_pddl,
            "action": "pick-up", "omitted": "(handempty) [learned omission]",
            "desc": "SAT learner omitted (handempty) and delete effect in pick-up"
        },
        "LOCM2 Learned Model": {
            "pddl": locm2_pddl,
            "action": "all", "omitted": "missing deletes & corrupted preconditions",
            "desc": "FSM learner lacks delete effects and conflates relations"
        }
    }

def run_full_proposition1_matrix() -> dict[str, Any]:
    """Runs all 12 model configurations across all 3 benchmark tasks."""
    gt_file = "benchmark_outputs/ground_truth.pddl"
    with open(gt_file, "r", encoding="utf-8") as f:
        gt_pddl = f.read()
    gt_models = parse_pddl_model(gt_pddl)

    tasks = get_benchmark_tasks()
    interventions = get_precondition_interventions(gt_pddl)

    suite_results = {}

    for int_name, int_config in interventions.items():
        pddl_text = int_config["pddl"]
        model = parse_pddl_model(pddl_text)

        # 1. Passive Transition Prediction Accuracy on genuine 100 test transitions
        t_eval = evaluate_transition_accuracy(pddl_text)
        a_pred = t_eval["a_pred"]

        int_results = {
            "action": int_config["action"],
            "omitted": int_config["omitted"],
            "description": int_config["desc"],
            "A_pred": a_pred,
            "tasks": {}
        }

        # 2. Evaluate planning and execution across all tasks
        for task_name, task_data in tasks.items():
            planner = PDDLForwardPlanner(model, task_data["objects"])
            plan, _nodes = planner.solve(task_data["init"], task_data["goal"])

            phantom_edges = 0
            if plan:
                sim_state = set(task_data["init"])
                for act_name, args in plan:
                    gt_schema = gt_models[act_name]
                    pmap = {p: a for p, a in zip(gt_schema.params, args)}
                    if not gt_schema.is_applicable(sim_state, pmap):
                        phantom_edges += 1
                    lrn_schema = model[act_name]
                    lrn_pmap = {p: a for p, a in zip(lrn_schema.params, args)}
                    sim_state = lrn_schema.apply(sim_state, lrn_pmap)

                success, _steps, fail_reason = planner.execute_plan(
                    task_data["init"], plan, gt_models, task_data["goal"]
                )
                pesr = 1.0 if success else 0.0
                plan_cost = len(plan)
                opt_cost = task_data["optimal_cost"]
                r_play = str(max(0, plan_cost - opt_cost)) if success else "INFINITY"
            else:
                success, _steps, fail_reason = False, 0, "No plan found"
                pesr = 0.0
                r_play = "INFINITY"

            int_results["tasks"][task_name] = {
                "plan_found": plan is not None,
                "plan_length": len(plan) if plan else 0,
                "phantom_edges": phantom_edges,
                "PESR": pesr,
                "R_play": r_play,
                "fail_reason": fail_reason,
                "plan_str": " -> ".join([f"{a[0]}({','.join(a[1])})" for a in plan]) if plan else "None"
            }

        suite_results[int_name] = int_results

    return suite_results

def print_full_matrix_report(results: dict[str, Any]):
    print("\n" + "="*125)
    print("PHASE 3: EXHAUSTIVE PROPOSITION 1 EXPERIMENTAL MATRIX (ALL 9 PRECONDITION OMISSIONS + LEARNED MODELS)")
    print("="*125)
    header = f"{'Intervention Condition':<35} | {'A_pred':<7} | {'Task 1 (Invert)':<22} | {'Task 2 (Disassemble)':<22} | {'Task 3 (Reassemble)':<22}"
    print(header)
    print(f"{'':<35} | {'':<7} | {'PESR | R_play | Phantom':<22} | {'PESR | R_play | Phantom':<22} | {'PESR | R_play | Phantom':<22}")
    print("-" * 125)

    for name, r in results.items():
        t1 = r["tasks"]["Task 1: Tower Inversion"]
        t2 = r["tasks"]["Task 2: Disassembly to Table"]
        t3 = r["tasks"]["Task 3: Reassembly from Table"]

        s1 = f"{t1['PESR']:.1f}  | {t1['R_play']:<8} | {t1['phantom_edges']}"
        s2 = f"{t2['PESR']:.1f}  | {t2['R_play']:<8} | {t2['phantom_edges']}"
        s3 = f"{t3['PESR']:.1f}  | {t3['R_play']:<8} | {t3['phantom_edges']}"

        print(f"{name[:35]:<35} | {r['A_pred']:<7.3f} | {s1:<22} | {s2:<22} | {s3:<22}")

    print("="*125)

run_precondition_intervention_suite = run_full_proposition1_matrix

if __name__ == "__main__":
    matrix_results = run_full_proposition1_matrix()

    print_full_matrix_report(matrix_results)
    with open("benchmark_outputs/proposition1_full_matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix_results, f, indent=2)
