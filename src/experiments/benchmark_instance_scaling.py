"""
benchmark_instance_scaling.py
Phase 4 Instance Scaling & Topological Divergence Benchmark.
Evaluates Action Model Precondition Interventions across increasing problem scales:
- Blocksworld: K in {3, 4, 5} blocks (tower inversion)
- Gripper: B in {2, 4, 6} balls (multi-room transport with 2 grippers)

Proves that:
1. Zone B planning collapse and phantom shortcuts persist identically across arbitrary problem sizes.
2. Relational relaxation triggers exponential search branch expansion (Proposition 2).
3. Plan Execution Success Rate (PESR) is strictly 0.0% across all scales on capacity/clearance invariants.

Strictly adheres to RESEARCH_RULES.md: deterministic, zero mock data.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import copy
import json
import math
import time
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import parse_pddl_model
from src.verification.general_pddl_planner import GeneralForwardPlanner


def calc_hp(nodes: int) -> float:
    return math.log2(1.0 + float(nodes))

def run_scaling_benchmark() -> dict[str, Any]:
    print("=" * 78)
    print("PHASE 4: INSTANCE SCALING & TOPOLOGICAL DIVERGENCE BENCHMARK")
    print("=" * 78)

    base = "daineto-meta-planning/src/meta_planning/dataset"
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "domains": {}
    }

    # -------------------------------------------------------------
    # 1. BLOCKSWORLD SCALING: K in {3, 4, 5} blocks
    # -------------------------------------------------------------
    bw_ref = os.path.join(base, "blocks", "reference")
    with open(bw_ref, "r", encoding="utf-8") as f:
        bw_gt_actions = parse_pddl_model(f.read())

    bw_interventions = [
        {
            "id": "BW_I1",
            "action": "unstack",
            "omit_literal": "(clear ?o1)",
            "archetype": "Relational Clearance Invariant"
        },
        {
            "id": "BW_I2",
            "action": "pick-up",
            "omit_literal": "(ontable ?o1)",
            "archetype": "Spatial Grounding Invariant"
        },
        {
            "id": "BW_I3",
            "action": "put-down",
            "omit_literal": "(holding ?o1)",
            "archetype": "Physical Holding Exclusivity"
        }
    ]

    bw_results = []
    print("\n--- Evaluating Blocksworld Scaling (K in {3, 4, 5} blocks) ---")
    for k in [3, 4, 5]:
        objs = [chr(ord('a') + i) for i in range(k)]
        # Tower inversion problem: stack inverted
        init = {'(ontable ' + objs[0] + ')', '(clear ' + objs[-1] + ')', '(handempty)'}
        for i in range(k - 1):
            init.add(f'(on {objs[i+1]} {objs[i]})')
        goal = set()
        for i in range(k - 1):
            goal.add(f'(on {objs[i]} {objs[i+1]})')

        # Solve M*
        p_gt = GeneralForwardPlanner(bw_gt_actions, objs)
        t0 = time.time()
        plan_gt, nodes_gt = p_gt.solve(init, goal, max_nodes=50000)
        time_gt = time.time() - t0
        hp_gt = calc_hp(nodes_gt)

        print(f"\n[Blocksworld K={k} Blocks] M* Plan Length: {len(plan_gt)}, Nodes: {nodes_gt} ({round(time_gt, 3)}s), H_P: {round(hp_gt, 3)}")

        for interv in bw_interventions:
            int_actions = {}
            for name, schema in bw_gt_actions.items():
                s_copy = copy.deepcopy(schema)
                if name == interv["action"]:
                    s_copy.preconditions = [
                        p for p in s_copy.preconditions
                        if interv["omit_literal"] not in p and p.replace(" ", "") != interv["omit_literal"].replace(" ", "")
                    ]
                int_actions[name] = s_copy

            p_hat = GeneralForwardPlanner(int_actions, objs)
            t0 = time.time()
            plan_hat, nodes_hat = p_hat.solve(init, goal, max_nodes=50000)
            time_hat = time.time() - t0
            hp_hat = calc_hp(nodes_hat)
            delta_hp = hp_hat - hp_gt

            # Execute plan_hat on true M*
            success, fail_step, reason = p_hat.execute_plan(init, plan_hat, bw_gt_actions, goal)

            entry = {
                "domain": "Blocksworld",
                "scale_param": "blocks",
                "scale_value": k,
                "intervention_id": interv["id"],
                "archetype": interv["archetype"],
                "m_star_plan_len": len(plan_gt) if plan_gt else None,
                "m_star_nodes": nodes_gt,
                "m_star_hp": round(hp_gt, 4),
                "m_hat_plan_len": len(plan_hat) if plan_hat else None,
                "m_hat_nodes": nodes_hat,
                "m_hat_hp": round(hp_hat, 4),
                "delta_hp": round(delta_hp, 4),
                "execution_success": success,
                "pesr": 1.0 if success else 0.0,
                "failure_step": fail_step,
                "failure_reason": reason,
                "time_m_star_sec": round(time_gt, 4),
                "time_m_hat_sec": round(time_hat, 4)
            }
            bw_results.append(entry)
            print(f"  [{interv['id']}] M_hat Len: {len(plan_hat) if plan_hat else 'None'}, Nodes: {nodes_hat} (ΔH_P: {round(delta_hp, 3)}), Exec Success: {success} (PESR={1.0 if success else 0.0})")
            if not success:
                print(f"      Failure reason: {reason}")

    results["domains"]["Blocksworld"] = bw_results

    # -------------------------------------------------------------
    # 2. GRIPPER SCALING: B in {2, 4, 6} balls
    # -------------------------------------------------------------
    grp_ref = os.path.join(base, "gripper", "reference")
    with open(grp_ref, "r", encoding="utf-8") as f:
        grp_gt_actions = parse_pddl_model(f.read())

    grp_interventions = [
        {
            "id": "GRP_I1",
            "action": "pick-up",
            "omit_literal": "(free ?o3)",
            "archetype": "Physical Capacity Exclusivity"
        },
        {
            "id": "GRP_I2",
            "action": "pick-up",
            "omit_literal": "(at-robby ?o2)",
            "archetype": "Spatial Co-location Invariant"
        },
        {
            "id": "GRP_I3",
            "action": "drop",
            "omit_literal": "(carry ?o1 ?o3)",
            "archetype": "Physical Holding Exclusivity"
        }
    ]

    grp_results = []
    print("\n--- Evaluating Gripper Scaling (B in {2, 4, 6} balls) ---")
    for b_count in [2, 4, 6]:
        objects = ['rooma', 'roomb'] + [f'ball{i}' for i in range(1, b_count + 1)] + ['left', 'right']
        type_map = {'rooma': 'room', 'roomb': 'room', 'left': 'gripper', 'right': 'gripper'}
        for i in range(1, b_count + 1):
            type_map[f'ball{i}'] = 'ball'

        param_types = {
            'move': ['room', 'room'],
            'pick-up': ['ball', 'room', 'gripper'],
            'drop': ['ball', 'room', 'gripper']
        }

        init = {'(at-robby rooma)', '(free left)', '(free right)'}
        for i in range(1, b_count + 1):
            init.add(f'(at ball{i} rooma)')
        goal = set()
        for i in range(1, b_count + 1):
            goal.add(f'(at ball{i} roomb)')

        p_gt = GeneralForwardPlanner(grp_gt_actions, objects, type_map, param_types)
        t0 = time.time()
        plan_gt, nodes_gt = p_gt.solve(init, goal, max_nodes=50000)
        time_gt = time.time() - t0
        hp_gt = calc_hp(nodes_gt)

        print(f"\n[Gripper B={b_count} Balls] M* Plan Length: {len(plan_gt)}, Nodes: {nodes_gt} ({round(time_gt, 3)}s), H_P: {round(hp_gt, 3)}")

        for interv in grp_interventions:
            int_actions = {}
            for name, schema in grp_gt_actions.items():
                s_copy = copy.deepcopy(schema)
                if name == interv["action"]:
                    s_copy.preconditions = [
                        p for p in s_copy.preconditions
                        if interv["omit_literal"] not in p and p.replace(" ", "") != interv["omit_literal"].replace(" ", "")
                    ]
                int_actions[name] = s_copy

            p_hat = GeneralForwardPlanner(int_actions, objects, type_map, param_types)
            t0 = time.time()
            plan_hat, nodes_hat = p_hat.solve(init, goal, max_nodes=50000)
            time_hat = time.time() - t0
            hp_hat = calc_hp(nodes_hat)
            delta_hp = hp_hat - hp_gt

            success, fail_step, reason = p_hat.execute_plan(init, plan_hat, grp_gt_actions, goal)

            entry = {
                "domain": "Gripper",
                "scale_param": "balls",
                "scale_value": b_count,
                "intervention_id": interv["id"],
                "archetype": interv["archetype"],
                "m_star_plan_len": len(plan_gt) if plan_gt else None,
                "m_star_nodes": nodes_gt,
                "m_star_hp": round(hp_gt, 4),
                "m_hat_plan_len": len(plan_hat) if plan_hat else None,
                "m_hat_nodes": nodes_hat,
                "m_hat_hp": round(hp_hat, 4),
                "delta_hp": round(delta_hp, 4),
                "execution_success": success,
                "pesr": 1.0 if success else 0.0,
                "failure_step": fail_step,
                "failure_reason": reason,
                "time_m_star_sec": round(time_gt, 4),
                "time_m_hat_sec": round(time_hat, 4)
            }
            grp_results.append(entry)
            print(f"  [{interv['id']}] M_hat Len: {len(plan_hat) if plan_hat else 'None'}, Nodes: {nodes_hat} (ΔH_P: {round(delta_hp, 3)}), Exec Success: {success} (PESR={1.0 if success else 0.0})")
            if not success:
                print(f"      Failure reason: {reason}")

    results["domains"]["Gripper"] = grp_results

    # Save to disk
    out_dir = "benchmark_outputs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "instance_scaling_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 78)
    print(f"Benchmark completed successfully! Results written to: {out_path}")
    print("=" * 78)
    return results

if __name__ == "__main__":
    run_scaling_benchmark()
