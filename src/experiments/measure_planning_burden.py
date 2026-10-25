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
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import ActionSchema, parse_pddl_model, safe_ground
from src.verification.general_pddl_planner import GeneralForwardPlanner


def get_full_24intervention_matrix(
    config_path: str = "configs/interventions/matrix_24.yaml",
) -> dict[str, dict[str, Any]]:
    """Loads the canonical 24 intervention matrix across 8 IPC domains from YAML configuration."""
    cfg_p = Path(config_path)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_path
    data = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    domains = data["domains"]
    for dom_cfg in domains.values():
        if isinstance(dom_cfg.get("init"), list):
            dom_cfg["init"] = set(dom_cfg["init"])
        if isinstance(dom_cfg.get("goal"), list):
            dom_cfg["goal"] = set(dom_cfg["goal"])
    return domains

def run_planning_burden_suite(config_path: str = "configs/interventions/matrix_24.yaml") -> dict[str, Any]:
    print("=" * 78)
    print("PHASE 4 WEEK 2: MEASURING PLANNING BURDEN H_P ACROSS 24 INTERVENTIONS")
    print("=" * 78)

    matrix = get_full_24intervention_matrix(config_path)
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

        with open(ref_file, encoding="utf-8") as f:
            ref_text = f.read()

        gt_models = parse_pddl_model(ref_text)
        gt_planner = GeneralForwardPlanner(gt_models, objects)

        # 1. Compute H_P on Ground Truth Model M*
        gt_plan, gt_nodes = gt_planner.solve(init, goal)
        gt_hp = math.log2(1.0 + float(gt_nodes))
        gt_sol_len = len(gt_plan) if gt_plan else 0
        gt_valid, _gt_steps, gt_err = gt_planner.execute_plan(init, gt_plan, gt_models, goal)
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
            for k_act in gt_models:
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
            gt_exec_valid, _exec_steps, failure_reason = gt_planner.execute_plan(init, lrn_plan, gt_models, goal)
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
