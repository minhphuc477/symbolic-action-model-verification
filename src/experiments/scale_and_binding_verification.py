"""
scale_and_binding_verification.py
Phase 4 Week 2 Remediation & Deep Verification Suite:
1. Empirical Scale Verification: Evaluates H_P and Delta H_P across increasing problem sizes
   - Blocksworld: N = 3, 4, 5 blocks (exponential detour explosion)
   - Hanoi: N = 2, 3 disks (amplifying phantom shortcut)
2. Binding Precondition Verification: Demonstrates that the 8 PESR=1.0 interventions fail completely
   (PESR = 0.0, R_play = INFINITY) when evaluated on non-degenerate / non-colocated / multi-capacity tasks.
Strictly adheres to RESEARCH_RULES.md: zero fake metrics, fully deterministic.
"""

import json
import math
import os
import sys
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import ActionSchema, parse_pddl_model
from src.verification.general_pddl_planner import GeneralForwardPlanner


def run_scale_verification() -> dict[str, Any]:
    print("=" * 78)
    print("1. EMPIRICAL SCALE VERIFICATION (BLOCKSWORLD & HANOI)")
    print("=" * 78)
    
    scale_data = {"blocksworld": [], "hanoi": []}
    
    # 1. Blocksworld Scaling (Tower Inversion)
    bw_ref = "daineto-meta-planning/src/meta_planning/dataset/blocks/reference"
    with open(bw_ref, "r", encoding="utf-8") as f:
        bw_gt = parse_pddl_model(f.read())
        
    print("\n--- Blocksworld Scaling (Phantom Detour BW_I1: omit clear ?o1) ---")
    print(f"{'Blocks':<8} | {'GT Nodes':<10} | {'GT H_P':<8} | {'Intv Nodes':<12} | {'Intv H_P':<8} | {'Delta H_P':<10} | {'PESR':<6}")
    print("-" * 72)
    
    for n in [3, 4, 5]:
        blocks = [chr(ord('a') + i) for i in range(n)]
        init = set()
        init.add('(handempty)')
        init.add(f'(ontable {blocks[0]})')
        for i in range(1, n):
            init.add(f'(on {blocks[i]} {blocks[i-1]})')
        init.add(f'(clear {blocks[-1]})')
        
        goal = set()
        goal.add(f'(ontable {blocks[-1]})')
        for i in range(n - 1):
            goal.add(f'(on {blocks[i]} {blocks[i+1]})')
        goal.add(f'(clear {blocks[0]})')
        
        gt_planner = GeneralForwardPlanner(bw_gt, blocks)
        _gt_plan, gt_nodes = gt_planner.solve(init, goal, max_nodes=100000)
        gt_hp = math.log2(1.0 + float(gt_nodes))
        
        # Intervene BW_I1: omit clear in unstack
        int_models = dict(bw_gt)
        old = bw_gt['unstack']
        new_pre = [p for p in old.preconditions if p.strip().lower() != '(clear ?o1)']
        raw_eff = old.add_effects + [f'(not {d})' for d in old.del_effects]
        int_models['unstack'] = ActionSchema(old.name, old.params, new_pre, raw_eff)
        
        int_planner = GeneralForwardPlanner(int_models, blocks)
        int_plan, int_nodes = int_planner.solve(init, goal, max_nodes=100000)
        int_hp = math.log2(1.0 + float(int_nodes))
        delta_hp = int_hp - gt_hp
        
        valid, _steps, reason = gt_planner.execute_plan(init, int_plan, bw_gt, goal)
        pesr = 1.0 if valid else 0.0
        
        rec = {
            "n_blocks": n,
            "gt_nodes": gt_nodes,
            "gt_hp": round(gt_hp, 3),
            "intv_nodes": int_nodes,
            "intv_hp": round(int_hp, 3),
            "delta_hp": round(delta_hp, 3),
            "pesr": pesr,
            "execution_failure_reason": reason
        }
        scale_data["blocksworld"].append(rec)
        print(f"{n:<8} | {gt_nodes:<10} | {gt_hp:<8.3f} | {int_nodes:<12} | {int_hp:<8.3f} | {delta_hp:<+10.3f} | {pesr:<6.1f}")
        
    # 2. Hanoi Scaling (Tower Transfer)
    han_ref = "daineto-meta-planning/src/meta_planning/dataset/hanoi/reference"
    with open(han_ref, "r", encoding="utf-8") as f:
        han_gt = parse_pddl_model(f.read())
        
    print("\n--- Hanoi Scaling (Phantom Shortcut HAN_I2: omit clear ?o1) ---")
    print(f"{'Disks':<8} | {'GT Nodes':<10} | {'GT H_P':<8} | {'Intv Nodes':<12} | {'Intv H_P':<8} | {'Delta H_P':<10} | {'PESR':<6}")
    print("-" * 72)
    
    for n in [2, 3]:
        disks = [f'd{i}' for i in range(1, n + 1)]
        pegs = ['p1', 'p2', 'p3']
        objs = disks + pegs
        init = set()
        for p in pegs:
            for d in disks:
                init.add(f'(smaller {p} {d})')
        for i in range(len(disks)):
            for j in range(i + 1, len(disks)):
                init.add(f'(smaller {disks[j]} {disks[i]})')
        
        init.add('(clear d1)')
        init.add('(clear p2)')
        init.add('(clear p3)')
        for i in range(len(disks) - 1):
            init.add(f'(on {disks[i]} {disks[i+1]})')
        init.add(f'(on {disks[-1]} p1)')
        
        goal = set()
        for i in range(len(disks) - 1):
            goal.add(f'(on {disks[i]} {disks[i+1]})')
        goal.add(f'(on {disks[-1]} p3)')
        
        gt_planner = GeneralForwardPlanner(han_gt, objs)
        _gt_plan, gt_nodes = gt_planner.solve(init, goal, max_nodes=50000)
        gt_hp = math.log2(1.0 + float(gt_nodes))
        
        # Intervene HAN_I2: omit clear ?o1
        int_models = dict(han_gt)
        old = han_gt['move']
        new_pre = [p for p in old.preconditions if p.strip().lower() != '(clear ?o1)']
        raw_eff = old.add_effects + [f'(not {d})' for d in old.del_effects]
        int_models['move'] = ActionSchema(old.name, old.params, new_pre, raw_eff)
        
        int_planner = GeneralForwardPlanner(int_models, objs)
        int_plan, int_nodes = int_planner.solve(init, goal, max_nodes=50000)
        int_hp = math.log2(1.0 + float(int_nodes))
        delta_hp = int_hp - gt_hp
        
        valid, _steps, reason = gt_planner.execute_plan(init, int_plan, han_gt, goal)
        pesr = 1.0 if valid else 0.0
        
        rec = {
            "n_disks": n,
            "gt_nodes": gt_nodes,
            "gt_hp": round(gt_hp, 3),
            "intv_nodes": int_nodes,
            "intv_hp": round(int_hp, 3),
            "delta_hp": round(delta_hp, 3),
            "pesr": pesr,
            "execution_failure_reason": reason
        }
        scale_data["hanoi"].append(rec)
        print(f"{n:<8} | {gt_nodes:<10} | {gt_hp:<8.3f} | {int_nodes:<12} | {int_hp:<8.3f} | {delta_hp:<+10.3f} | {pesr:<6.1f}")
        
    return scale_data

def run_binding_precondition_suite() -> dict[str, Any]:
    print("\n" + "=" * 78)
    print("2. BINDING PRECONDITION VERIFICATION FOR THE 8 PESR=1.0 INTERVENTIONS")
    print("=" * 78)
    
    binding_results = {}
    
    # Define non-degenerate test tasks that exercise the omitted precondition
    # 1. Miconic MIC_I1 (omit lift-at): passenger at f2, lift at f1
    mic_ref = "daineto-meta-planning/src/meta_planning/dataset/miconic/reference"
    mic_gt = parse_pddl_model(Path(mic_ref).read_text(encoding="utf-8"))
    objs = ['f1', 'f2', 'f3', 'p1']
    init = {'(lift-at f1)', '(origin p1 f2)', '(destin p1 f3)', '(above f1 f2)', '(above f2 f3)', '(above f1 f3)'}
    goal = {'(served p1)'}
    
    int_models = dict(mic_gt)
    old = mic_gt['board']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(lift-at ?o1)']
    int_models['board'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    
    p_gt = GeneralForwardPlanner(mic_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, mic_gt, goal)
    binding_results["MIC_I1"] = {
        "domain": "Miconic",
        "action": "board",
        "precondition": "(lift-at ?o1)",
        "task_setup": "Non-colocated passenger (lift at f1, passenger origin f2)",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"MIC_I1 (Non-colocated origin) -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")
    
    # 2. Driverlog DLG_I3 (omit at ?o1 ?o3 in load-truck): pkg1 at s1, truck at s0
    dlg_ref = "daineto-meta-planning/src/meta_planning/dataset/driverlog/reference"
    dlg_gt = parse_pddl_model(Path(dlg_ref).read_text(encoding="utf-8"))
    objs = ['driver1', 'truck1', 'pkg1', 's0', 's1']
    init = {'(at driver1 s0)', '(at truck1 s0)', '(at pkg1 s1)', '(empty truck1)', '(link s0 s1)', '(link s1 s0)'}
    goal = {'(at pkg1 s0)'}
    
    int_models = dict(dlg_gt)
    old = dlg_gt['load-truck']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(at ?o1 ?o3)']
    int_models['load-truck'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    
    p_gt = GeneralForwardPlanner(dlg_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, dlg_gt, goal)
    binding_results["DLG_I3"] = {
        "domain": "Driverlog",
        "action": "load-truck",
        "precondition": "(at ?o1 ?o3)",
        "task_setup": "Remote package (truck at s0, package at s1)",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"DLG_I3 (Remote package)      -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")
    
    # 3. Blocksworld BW_I2 (omit ontable in pick-up): block b is stacked on a, goal requires holding b
    bw_ref = "daineto-meta-planning/src/meta_planning/dataset/blocks/reference"
    bw_gt = parse_pddl_model(Path(bw_ref).read_text(encoding="utf-8"))
    objs = ['a', 'b']
    init = {'(ontable a)', '(on b a)', '(clear b)', '(handempty)'}
    goal = {'(holding b)'}
    
    int_models = dict(bw_gt)
    old = bw_gt['pick-up']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(ontable ?o1)']
    int_models['pick-up'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    
    p_gt = GeneralForwardPlanner(bw_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, bw_gt, goal)
    binding_results["BW_I2"] = {
        "domain": "Blocksworld",
        "action": "pick-up",
        "precondition": "(ontable ?o1)",
        "task_setup": "Stacked block pick-up (b stacked on a, picking up without unstacking)",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"BW_I2  (Stacked pick-up)     -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    # 4. Miconic MIC_I3 (omit above ?o1 ?o2 in up): elevator moving downwards using 'up'
    objs = ['f1', 'f2', 'f3', 'p1']
    init = {'(lift-at f3)', '(origin p1 f3)', '(destin p1 f1)', '(above f1 f2)', '(above f2 f3)', '(above f1 f3)'}
    goal = {'(served p1)'}
    int_models = dict(mic_gt)
    old = mic_gt['up']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(above ?o1 ?o2)']
    int_models['up'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    p_gt = GeneralForwardPlanner(mic_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, mic_gt, goal)
    binding_results["MIC_I3"] = {
        "domain": "Miconic",
        "action": "up",
        "precondition": "(above ?o1 ?o2)",
        "task_setup": "Downwards journey using unconstrained 'up' action",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"MIC_I3 (Reverse 'up' action) -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    # 5. Satellite SAT_I1 (omit power-avail in switch-on): 2 instruments requiring power
    sat_ref = "daineto-meta-planning/src/meta_planning/dataset/satellite/reference"
    sat_gt = parse_pddl_model(Path(sat_ref).read_text(encoding="utf-8"))
    objs = ['sat1', 'dir0', 'dir1', 'cam1', 'cam2', 'mode1']
    init = {
        '(on-board cam1 sat1)', '(supports cam1 mode1)',
        '(on-board cam2 sat1)', '(supports cam2 mode1)',
        '(power-avail sat1)', '(pointing sat1 dir0)',
        '(calibration-target cam1 dir0)', '(calibration-target cam2 dir0)'
    }
    goal = {'(power-on cam1)', '(power-on cam2)'}
    int_models = dict(sat_gt)
    old = sat_gt['switch-on']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(power-avail ?o2)']
    int_models['switch-on'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    p_gt = GeneralForwardPlanner(sat_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, sat_gt, goal)
    binding_results["SAT_I1"] = {
        "domain": "Satellite",
        "action": "switch-on",
        "precondition": "(power-avail ?o2)",
        "task_setup": "Dual instrument power draw exceeding satellite capacity",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"SAT_I1 (Dual power draw)    -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    # 6. Hanoi HAN_I1 (omit smaller in move): goal where illegal stacking is a shortcut
    objs = ['d1', 'd2', 'p1', 'p2', 'p3']
    init = {
        '(smaller p1 d1)', '(smaller p2 d1)', '(smaller p3 d1)',
        '(smaller p1 d2)', '(smaller p2 d2)', '(smaller p3 d2)',
        '(smaller d2 d1)',
        '(clear d1)', '(clear p2)', '(clear p3)',
        '(on d1 d2)', '(on d2 p1)'
    }
    goal = {'(on d2 d1)'}
    han_ref = "daineto-meta-planning/src/meta_planning/dataset/hanoi/reference"
    han_gt = parse_pddl_model(Path(han_ref).read_text(encoding="utf-8"))
    int_models = dict(han_gt)
    old = han_gt['move']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(smaller ?o3 ?o1)']
    int_models['move'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    p_gt = GeneralForwardPlanner(han_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, han_gt, goal)
    binding_results["HAN_I1"] = {
        "domain": "Hanoi",
        "action": "move",
        "precondition": "(smaller ?o3 ?o1)",
        "task_setup": "Direct placement of larger disk on smaller disk",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"HAN_I1 (Inverted disk stack) -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    # 7. Rovers ROV_I2 (omit empty ?o2 in sample-soil): store is full initially
    rov_ref = "daineto-meta-planning/src/meta_planning/dataset/rovers/reference"
    rov_gt = parse_pddl_model(Path(rov_ref).read_text(encoding="utf-8"))
    objs = ['rover1', 'w1', 's1']
    init = {
        '(at rover1 w1)', '(available rover1)', '(equipped-for-soil-analysis rover1)',
        '(store-of s1 rover1)', '(full s1)', '(at-soil-sample w1)'
    }
    goal = {'(have-soil-analysis rover1 w1)'}
    int_models = dict(rov_gt)
    old = rov_gt['sample-soil']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(empty ?o2)']
    int_models['sample-soil'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    p_gt = GeneralForwardPlanner(rov_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, rov_gt, goal)
    binding_results["ROV_I2"] = {
        "domain": "Rovers",
        "action": "sample-soil",
        "precondition": "(empty ?o2)",
        "task_setup": "Sample into already full storage container",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"ROV_I2 (Full store sample)  -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    # 8. Rovers ROV_I3 (omit available in communicate-soil-data): rover is busy
    objs = ['rover1', 'w1', 's1', 'l1']
    init = {
        '(at rover1 w1)', '(at-lander l1 w1)', '(have-soil-analysis rover1 w1)',
        '(visible w1 w1)', '(channel-free l1)'
    }
    goal = {'(communicated-soil-data w1)'}
    int_models = dict(rov_gt)
    old = rov_gt['communicate-soil-data']
    new_pre = [p for p in old.preconditions if p.strip().lower() != '(available ?o1)']
    int_models['communicate-soil-data'] = ActionSchema(old.name, old.params, new_pre, old.add_effects + [f'(not {d})' for d in old.del_effects])
    p_gt = GeneralForwardPlanner(rov_gt, objs)
    p_int = GeneralForwardPlanner(int_models, objs)
    plan, _nodes = p_int.solve(init, goal)
    valid, _steps, reason = p_gt.execute_plan(init, plan, rov_gt, goal)
    binding_results["ROV_I3"] = {
        "domain": "Rovers",
        "action": "communicate-soil-data",
        "precondition": "(available ?o1)",
        "task_setup": "Data transmission while transceiver hardware is locked",
        "pesr": 1.0 if valid else 0.0,
        "r_play": "0.0" if valid else "INFINITY",
        "failure_reason": reason
    }
    print(f"ROV_I3 (Locked transceiver) -> PESR: {1.0 if valid else 0.0} | Reason: {reason}")

    out_file = os.path.join(os.path.dirname(__file__), "../../benchmark_outputs/scale_and_binding_results.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    all_data = {
        "scale_verification": run_scale_verification(),
        "binding_verification": binding_results
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print(f"\nAll verification data saved to: {out_file}")
    return all_data

if __name__ == "__main__":
    run_binding_precondition_suite()
