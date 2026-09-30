"""
measure_planning_burden.py
Phase 4 Week 2 Deliverable:
Measures Planning Burden H_P(M*, x) and H_P(M_hat, x) across all 24 interventions in the 8 IPC domains.
Strictly adheres to RESEARCH_RULES.md: deterministic, zero fake metrics.
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import time
import json
import math
from typing import Dict, Any, List, Set, Tuple, Optional

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import parse_pddl_model, ActionSchema, safe_ground
from src.verification.general_pddl_planner import GeneralForwardPlanner
from src.metrics.planning_burden import compute_planning_burden

def get_full_24intervention_matrix() -> Dict[str, Dict[str, Any]]:
    base = "daineto-meta-planning/src/meta_planning/dataset"

    return {
        "Blocksworld": {
            "ref_file": os.path.join(base, "blocks", "reference"),
            "objects": ["a", "b", "c"],
            "init": {"(on c b)", "(on b a)", "(ontable a)", "(clear c)", "(handempty)"},
            "goal": {"(on a b)", "(on b c)"},
            "interventions": [
                {
                    "id": "BW_I1",
                    "action": "unstack",
                    "omit_literal": "(clear ?o1)",
                    "archetype": "Relational Recursive Clearance Invariant",
                    "description": "Omit clear condition on source block, allowing buried blocks to be unstacked"
                },
                {
                    "id": "BW_I2",
                    "action": "pick-up",
                    "omit_literal": "(ontable ?o1)",
                    "archetype": "Spatial Grounding Invariant",
                    "description": "Omit ontable condition, allowing picking up blocks floating in mid-air or stacked"
                },
                {
                    "id": "BW_I3",
                    "action": "put-down",
                    "omit_literal": "(holding ?o1)",
                    "archetype": "Physical Holding Exclusivity",
                    "description": "Omit holding condition, allowing putting down blocks without holding them"
                }
            ]
        },
        "Gripper": {
            "ref_file": os.path.join(base, "gripper", "reference"),
            "objects": ["rooma", "roomb", "ball1", "ball2", "left", "right"],
            "init": {"(at-robby rooma)", "(at ball1 rooma)", "(at ball2 rooma)", "(free left)", "(free right)"},
            "goal": {"(at ball1 roomb)", "(at ball2 roomb)"},
            "interventions": [
                {
                    "id": "GRP_I1",
                    "action": "pick-up",
                    "omit_literal": "(free ?o3)",
                    "archetype": "Physical Capacity Exclusivity",
                    "description": "Omit free condition, allowing multiple balls in one gripper"
                },
                {
                    "id": "GRP_I2",
                    "action": "pick-up",
                    "omit_literal": "(at-robby ?o2)",
                    "archetype": "Spatial Co-location Invariant",
                    "description": "Omit robot location check, allowing picking balls from remote rooms"
                },
                {
                    "id": "GRP_I3",
                    "action": "drop",
                    "omit_literal": "(carry ?o1 ?o3)",
                    "archetype": "Physical Holding Exclusivity",
                    "description": "Omit carry condition, allowing dropping balls not currently held"
                }
            ]
        },
        "Ferry": {
            "ref_file": os.path.join(base, "ferry", "reference"),
            "objects": ["c1", "c2", "l1", "l2"],
            "init": {"(at-ferry l1)", "(empty-ferry)", "(at c1 l1)", "(at c2 l1)", "(not-eq l1 l2)", "(not-eq l2 l1)"},
            "goal": {"(at c1 l2)", "(at c2 l2)"},
            "interventions": [
                {
                    "id": "FRY_I1",
                    "action": "board",
                    "omit_literal": "(empty-ferry)",
                    "archetype": "Physical Capacity Exclusivity",
                    "description": "Omit empty ferry constraint, allowing boarding unlimited cars"
                },
                {
                    "id": "FRY_I2",
                    "action": "board",
                    "omit_literal": "(at-ferry ?o2)",
                    "archetype": "Spatial Co-location Invariant",
                    "description": "Omit ferry location check, allowing boarding from remote ports"
                },
                {
                    "id": "FRY_I3",
                    "action": "debark",
                    "omit_literal": "(on ?o1)",
                    "archetype": "Vehicle Passenger Dependency",
                    "description": "Omit onboard requirement, allowing debarking cars not on ferry"
                }
            ]
        },
        "Miconic": {
            "ref_file": os.path.join(base, "miconic", "reference"),
            "objects": ["f1", "f2", "f3", "p1"],
            "init": {"(lift-at f1)", "(origin p1 f1)", "(destin p1 f3)", "(above f1 f2)", "(above f2 f3)", "(above f1 f3)"},
            "goal": {"(served p1)"},
            "interventions": [
                {
                    "id": "MIC_I1",
                    "action": "board",
                    "omit_literal": "(lift-at ?o1)",
                    "archetype": "Spatial Alignment Constraint",
                    "description": "Omit elevator floor alignment, allowing passenger boarding remotely"
                },
                {
                    "id": "MIC_I2",
                    "action": "depart",
                    "omit_literal": "(boarded ?o2)",
                    "archetype": "Passenger Boarding Dependency",
                    "description": "Omit boarded requirement, serving passenger without boarding"
                },
                {
                    "id": "MIC_I3",
                    "action": "up",
                    "omit_literal": "(above ?o1 ?o2)",
                    "archetype": "Directional Topological Invariant",
                    "description": "Omit above relation, allowing elevator to jump non-sequentially"
                }
            ]
        },
        "Driverlog": {
            "ref_file": os.path.join(base, "driverlog", "reference"),
            "objects": ["driver1", "truck1", "pkg1", "s0", "s1"],
            "init": {"(at driver1 s0)", "(at truck1 s0)", "(at pkg1 s0)", "(empty truck1)", "(link s0 s1)", "(link s1 s0)"},
            "goal": {"(at pkg1 s1)"},
            "interventions": [
                {
                    "id": "DLG_I1",
                    "action": "board-truck",
                    "omit_literal": "(empty ?o2)",
                    "archetype": "Driver Cabin Capacity Exclusivity",
                    "description": "Omit empty truck check, allowing multiple drivers in one truck"
                },
                {
                    "id": "DLG_I2",
                    "action": "drive-truck",
                    "omit_literal": "(driving ?o4 ?o1)",
                    "archetype": "Agent Dependency Constraint",
                    "description": "Omit driver presence, allowing ghost driving without a driver"
                },
                {
                    "id": "DLG_I3",
                    "action": "load-truck",
                    "omit_literal": "(at ?o1 ?o3)",
                    "archetype": "Spatial Co-location Invariant",
                    "description": "Omit package location check, allowing loading remote packages"
                }
            ]
        },
        "Hanoi": {
            "ref_file": os.path.join(base, "hanoi", "reference"),
            "objects": ["d1", "d2", "p1", "p2", "p3"],
            "init": {
                "(smaller p1 d1)", "(smaller p2 d1)", "(smaller p3 d1)",
                "(smaller p1 d2)", "(smaller p2 d2)", "(smaller p3 d2)",
                "(smaller d2 d1)",
                "(clear d1)", "(clear p2)", "(clear p3)",
                "(on d1 d2)", "(on d2 p1)"
            },
            "goal": {"(on d1 d2)", "(on d2 p3)"},
            "interventions": [
                {
                    "id": "HAN_I1",
                    "action": "move",
                    "omit_literal": "(smaller ?o3 ?o1)",
                    "archetype": "Disk Size Monotonicity Invariant",
                    "description": "Omit smaller check, allowing larger disk on smaller disk"
                },
                {
                    "id": "HAN_I2",
                    "action": "move",
                    "omit_literal": "(clear ?o1)",
                    "archetype": "Source Stack Clearance Invariant",
                    "description": "Omit source clear check, allowing pulling buried disks directly"
                },
                {
                    "id": "HAN_I3",
                    "action": "move",
                    "omit_literal": "(clear ?o3)",
                    "archetype": "Target Stack Clearance Invariant",
                    "description": "Omit destination clear check, allowing placing onto occupied top"
                }
            ]
        },
        "Satellite": {
            "ref_file": os.path.join(base, "satellite", "reference"),
            "objects": ["sat1", "dir0", "dir1", "cam1", "mode1"],
            "init": {
                "(on-board cam1 sat1)", "(supports cam1 mode1)",
                "(power-avail sat1)", "(pointing sat1 dir0)",
                "(calibration-target cam1 dir0)"
            },
            "goal": {"(have-image dir1 mode1)"},
            "interventions": [
                {
                    "id": "SAT_I1",
                    "action": "switch-on",
                    "omit_literal": "(power-avail ?o2)",
                    "archetype": "Power Resource Exclusivity",
                    "description": "Omit power availability check, allowing powering instruments without energy"
                },
                {
                    "id": "SAT_I2",
                    "action": "take-image",
                    "omit_literal": "(calibrated ?o3)",
                    "archetype": "Sensor Calibration State Lock",
                    "description": "Omit calibration requirement, taking scientific images uncalibrated"
                },
                {
                    "id": "SAT_I3",
                    "action": "take-image",
                    "omit_literal": "(pointing ?o1 ?o2)",
                    "archetype": "Directional Alignment Invariant",
                    "description": "Omit pointing alignment, imaging targets while pointing elsewhere"
                }
            ]
        },
        "Rovers": {
            "ref_file": os.path.join(base, "rovers", "reference"),
            "objects": ["rover1", "w1", "w2", "w3", "s1", "l1"],
            "init": {
                "(at rover1 w1)", "(available rover1)",
                "(can-traverse rover1 w1 w3)", "(visible w1 w3)", "(visible w3 w1)",
                "(can-traverse rover1 w3 w2)", "(visible w3 w2)", "(visible w2 w3)",
                "(visible w1 w2)", "(visible w2 w1)",
                "(equipped-for-soil-analysis rover1)", "(store-of s1 rover1)", "(empty s1)",
                "(at-soil-sample w2)", "(at-lander l1 w1)", "(channel-free l1)"
            },
            "goal": {"(communicated-soil-data w2)"},
            "interventions": [
                {
                    "id": "ROV_I1",
                    "action": "navigate",
                    "omit_literal": "(can-traverse ?o1 ?o2 ?o3)",
                    "archetype": "Topological Traversability Bottleneck",
                    "description": "Omit traversability check, teleporting across disconnected terrain"
                },
                {
                    "id": "ROV_I2",
                    "action": "sample-soil",
                    "omit_literal": "(empty ?o2)",
                    "archetype": "Hardware Storage Capacity Exclusivity",
                    "description": "Omit empty sample container, sampling repeatedly into full store"
                },
                {
                    "id": "ROV_I3",
                    "action": "communicate-soil-data",
                    "omit_literal": "(available ?o1)",
                    "archetype": "Transceiver Concurrency Invariant",
                    "description": "Omit rover availability check, transmitting data while bus is locked"
                }
            ]
        }
    }

def run_planning_burden_suite() -> Dict[str, Any]:
    print("=" * 78)
    print("PHASE 4 WEEK 2: MEASURING PLANNING BURDEN H_P ACROSS 24 INTERVENTIONS")
    print("=" * 78)

    matrix = get_full_24intervention_matrix()
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "domains": {}
    }

    total_interventions = 0
    phantom_shortcuts = 0
    phantom_detours = 0
    preserved_searches = 0
    execution_failures = 0

    for domain_name, dom_cfg in matrix.items():
        ref_file = dom_cfg["ref_file"]
        objects = dom_cfg["objects"]
        init = dom_cfg["init"]
        goal = dom_cfg["goal"]

        with open(ref_file, "r", encoding="utf-8") as f:
            ref_text = f.read()

        gt_models = parse_pddl_model(ref_text)
        gt_planner = GeneralForwardPlanner(gt_models, objects)

        # 1. Compute H_P on Ground Truth Model M*
        t0 = time.time()
        gt_plan, gt_nodes = gt_planner.solve(init, goal)
        gt_hp = math.log2(1.0 + float(gt_nodes))
        gt_sol_len = len(gt_plan) if gt_plan else 0
        gt_valid, gt_steps, gt_err = gt_planner.execute_plan(init, gt_plan, gt_models, goal)
        assert gt_valid, f"Ground truth for {domain_name} failed execution: {gt_err}"

        domain_entry = {
            "ground_truth": {
                "nodes_expanded": gt_nodes,
                "H_P": round(gt_hp, 4),
                "plan_length": gt_sol_len,
                "plan": [f"({a} {' '.join(args)})" for a, args in (gt_plan or [])]
            },
            "interventions": []
        }

        print(f"\n[{domain_name.upper()}] M* -> N_exp={gt_nodes}, H_P={gt_hp:.3f}, Path Len={gt_sol_len}")
        print("-" * 78)

        for int_spec in dom_cfg["interventions"]:
            total_interventions += 1
            int_id = int_spec["id"]
            act_name = int_spec["action"]
            omit_lit = int_spec["omit_literal"].strip().lower()
            archetype = int_spec["archetype"]

            # Construct intervened model M_hat
            intervened_models = dict(gt_models)
            found_act = False
            for k_act, schema in gt_models.items():
                if k_act.lower() == act_name.lower():
                    act_name = k_act
                    found_act = True
                    break
            assert found_act, f"Action {act_name} not found in {domain_name} model!"

            old_schema = gt_models[act_name]
            new_pre = [p for p in old_schema.preconditions if p.strip().lower() != omit_lit]
            assert len(new_pre) < len(old_schema.preconditions), f"Literal {omit_lit} not in preconditions of {act_name}!"
            raw_effects = old_schema.add_effects + [f"(not {d})" for d in old_schema.del_effects]
            intervened_models[act_name] = ActionSchema(
                old_schema.name, old_schema.params, new_pre, raw_effects
            )

            # Solve on M_hat
            lrn_planner = GeneralForwardPlanner(intervened_models, objects)
            lrn_plan, lrn_nodes = lrn_planner.solve(init, goal)
            lrn_hp = math.log2(1.0 + float(lrn_nodes))
            lrn_sol_len = len(lrn_plan) if lrn_plan else 0
            delta_hp = lrn_hp - gt_hp

            # Detect phantom edges in lrn_plan
            phantom_edges = []
            if lrn_plan:
                sim_state = set(init)
                for step_idx, (a_step, args) in enumerate(lrn_plan, start=1):
                    gt_sch = gt_models[a_step]
                    pmap = {p: a for p, a in zip(gt_sch.params, args)}
                    if not gt_sch.is_applicable(sim_state, pmap):
                        missing = [p for p in gt_sch.preconditions if safe_ground(p, pmap) not in sim_state]
                        phantom_edges.append({
                            "step": step_idx,
                            "action": f"({a_step} {' '.join(args)})",
                            "missing_literals": missing
                        })
                    next_s = intervened_models[a_step].apply(sim_state, pmap)
                    if next_s is not None:
                        sim_state = next_s

            # Execute lrn_plan on Ground Truth M*
            gt_exec_valid, exec_steps, failure_reason = gt_planner.execute_plan(init, lrn_plan, gt_models, goal)
            pesr = 1.0 if gt_exec_valid else 0.0
            r_play = 0.0 if gt_exec_valid else float("inf")

            if not gt_exec_valid:
                execution_failures += 1

            # Search Divergence Classification
            if delta_hp < -1e-5:
                divergence_type = "Phantom Shortcut"
                phantom_shortcuts += 1
            elif delta_hp > 1e-5:
                divergence_type = "Phantom Detour"
                phantom_detours += 1
            else:
                divergence_type = "Preserved Search"
                preserved_searches += 1

            int_record = {
                "id": int_id,
                "action": act_name,
                "omitted_precondition": omit_lit,
                "archetype": archetype,
                "description": int_spec["description"],
                "nodes_expanded": lrn_nodes,
                "H_P": round(lrn_hp, 4),
                "delta_H_P": round(delta_hp, 4),
                "plan_length": lrn_sol_len,
                "divergence_type": divergence_type,
                "phantom_edges_detected": len(phantom_edges),
                "phantom_edge_details": phantom_edges,
                "PESR": pesr,
                "R_play": "INFINITY" if math.isinf(r_play) else round(r_play, 4),
                "execution_failure_reason": failure_reason
            }
            domain_entry["interventions"].append(int_record)

            status_str = f"SHORTCUT (ΔH={delta_hp:+.2f})" if delta_hp < -1e-5 else (f"DETOUR (ΔH={delta_hp:+.2f})" if delta_hp > 1e-5 else "PRESERVED")
            pesr_str = "PESR=1.0" if pesr == 1.0 else "PESR=0.0 [R_play=∞]"
            print(f"  [{int_id}] Omit {omit_lit:<22} | N={lrn_nodes:<4} | H_P={lrn_hp:.3f} | {status_str:<22} | {pesr_str}")

        results["domains"][domain_name] = domain_entry

    results["summary"] = {
        "total_interventions": total_interventions,
        "phantom_shortcuts_count": phantom_shortcuts,
        "phantom_detours_count": phantom_detours,
        "preserved_searches_count": preserved_searches,
        "execution_failures_count": execution_failures,
        "decoupling_evidence_percentage": round(100.0 * execution_failures / total_interventions, 2)
    }

    out_file = os.path.join(os.path.dirname(__file__), "../../benchmark_outputs/planning_burden_results.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 78)
    print("PHASE 4 WEEK 2 SUITE COMPLETED SUCCESSFULLY")
    print(f"Output saved to: {out_file}")
    print(f"Summary: Total={total_interventions} | Shortcuts={phantom_shortcuts} | Detours={phantom_detours} | Preserved={preserved_searches} | Failures={execution_failures} (PESR=0.0)")
    print("=" * 78)

    return results

if __name__ == "__main__":
    run_planning_burden_suite()
