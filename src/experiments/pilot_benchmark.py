"""
pilot_benchmark.py
Pilot Benchmark for Phase 4:
1. Measures empirical execution runtimes of FAMA, LOCM2, and FastLAS on real learning tasks in WSL.
2. Formulates exact compute re-estimation based on empirical timings.
3. Tests and verifies candidate bottleneck preconditions across all 8 IPC domains:
   - Confirms plan existence on intervened model M_hat
   - Detects phantom edges
   - Executes step-by-step on Ground Truth physics M* to verify PESR = 0.0 and R_play = INFINITY.
Strictly adheres to RESEARCH_RULES.md: zero fake metrics, fully deterministic.
"""

import json
import os
import subprocess
import sys
import time
from typing import Any

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.metrics.transition_accuracy import ActionSchema, parse_pddl_model
from src.verification.general_pddl_planner import GeneralForwardPlanner


def benchmark_learners() -> dict[str, Any]:
    print("==================================================================")
    print("1. PILOT COMPUTE BENCHMARK: MEASURING REAL LEARNER RUNTIMES IN WSL")
    print("==================================================================")
    learner_timings = {}

    # 1. LOCM2
    print("Running LOCM2...")
    t0 = time.time()
    locm_cmd = ["wsl", "bash", "-c", "cd /mnt/f/Thesis/locm_repo && /mnt/f/Thesis/venv_linux/bin/python locm2.py"]
    res_locm = subprocess.run(locm_cmd, capture_output=True, text=True, check=False)
    t_locm = time.time() - t0
    learner_timings["LOCM2"] = {
        "runtime_seconds": round(t_locm, 3),
        "exit_code": res_locm.returncode,
        "output_summary": res_locm.stdout.strip().split("\n")[-1] if res_locm.stdout else "No stdout"
    }
    print(f"LOCM2 completed in {t_locm:.2f}s (Exit code: {res_locm.returncode})")

    # 2. FastLAS
    print("\nRunning FastLAS...")
    t0 = time.time()
    fastlas_cmd = ["wsl", "bash", "-c", "/mnt/f/Thesis/FastLAS_repo/FastLAS2/FastLAS /mnt/f/Thesis/test_fastlas_task.las"]
    res_fastlas = subprocess.run(fastlas_cmd, capture_output=True, text=True, check=False)
    t_fastlas = time.time() - t0
    learner_timings["FastLAS"] = {
        "runtime_seconds": round(t_fastlas, 3),
        "exit_code": res_fastlas.returncode,
        "output_summary": res_fastlas.stdout.strip().split("\n")[-1] if res_fastlas.stdout else "No stdout"
    }
    print(f"FastLAS completed in {t_fastlas:.2f}s (Exit code: {res_fastlas.returncode})")

    # 3. FAMA
    print("\nRunning FAMA (Madagascar SAT Planner)...")
    t0 = time.time()
    fama_cmd = ["wsl", "bash", "-c", "/mnt/f/Thesis/venv_linux/bin/python /mnt/f/Thesis/run_fama_test.py"]
    res_fama = subprocess.run(fama_cmd, capture_output=True, text=True, check=False)
    t_fama = time.time() - t0
    learner_timings["FAMA"] = {
        "runtime_seconds": round(t_fama, 3),
        "exit_code": res_fama.returncode,
        "output_summary": "FAMA SAT compilation complete" if "LEARNED PDDL DOMAIN MODEL:" in res_fama.stdout else "Execution logged"
    }
    print(f"FAMA completed in {t_fama:.2f}s (Exit code: {res_fama.returncode})")

    avg_time = (t_locm + t_fastlas + t_fama) / 3.0
    learner_timings["summary"] = {
        "avg_seconds_per_run": round(avg_time, 2),
        "total_864_runs_hours": round((864 * avg_time) / 3600.0, 2),
        "parallel_8cores_hours": round((864 * avg_time) / (3600.0 * 8.0), 2)
    }
    print(f"\nEmpirical Mean Learner Runtime: {avg_time:.2f}s per run")
    print(f"Projected Total Time for 864 runs: {learner_timings['summary']['total_864_runs_hours']} hours CPU ({learner_timings['summary']['parallel_8cores_hours']} hours on 8 cores)")

    return learner_timings

def get_8domain_configs() -> dict[str, dict[str, Any]]:
    """Defines ground truth paths, problem setups, and target bottleneck interventions for all 8 IPC domains."""
    base = "daineto-meta-planning/src/meta_planning/dataset"

    return {
        "Blocksworld": {
            "ref_file": os.path.join(base, "blocks", "reference"),
            "objects": ["a", "b", "c"],
            "init": {"(on c b)", "(on b a)", "(ontable a)", "(clear c)", "(handempty)"},
            "goal": {"(on a b)", "(on b c)"},
            "intervention": {
                "action": "unstack",
                "omit_literal": "(clear ?o1)",
                "type": "Relational Dependency Constraint"
            }
        },
        "Gripper": {
            "ref_file": os.path.join(base, "gripper", "reference"),
            "objects": ["rooma", "roomb", "ball1", "ball2", "left", "right"],
            "init": {"(at-robby rooma)", "(at ball1 rooma)", "(at ball2 rooma)", "(free left)", "(free right)"},
            "goal": {"(at ball1 roomb)", "(at ball2 roomb)"},
            "intervention": {
                "action": "pick-up",
                "omit_literal": "(free ?o3)",
                "type": "Physical Capacity Bottleneck"
            }
        },
        "Ferry": {
            "ref_file": os.path.join(base, "ferry", "reference"),
            "objects": ["c1", "c2", "l1", "l2"],
            "init": {"(at-ferry l1)", "(empty-ferry)", "(at c1 l1)", "(at c2 l1)", "(not-eq l1 l2)", "(not-eq l2 l1)"},
            "goal": {"(at c1 l2)", "(at c2 l2)"},
            "intervention": {
                "action": "board",
                "omit_literal": "(empty-ferry)",
                "type": "Physical Capacity Bottleneck"
            }
        },
        "Miconic": {
            "ref_file": os.path.join(base, "miconic", "reference"),
            "objects": ["f1", "f2", "f3", "p1"],
            "init": {"(lift-at f1)", "(origin p1 f1)", "(destin p1 f3)", "(above f1 f2)", "(above f2 f3)", "(above f1 f3)"},
            "goal": {"(served p1)"},
            "intervention": {
                "action": "depart",
                "omit_literal": "(boarded ?o2)",
                "type": "Status Dependency Lock"
            }
        },
        "Driverlog": {
            "ref_file": os.path.join(base, "driverlog", "reference"),
            "objects": ["driver1", "truck1", "pkg1", "s0", "s1"],
            "init": {"(at driver1 s0)", "(at truck1 s0)", "(at pkg1 s0)", "(empty truck1)", "(link s0 s1)", "(link s1 s0)"},
            "goal": {"(at pkg1 s1)"},
            "intervention": {
                "action": "drive-truck",
                "omit_literal": "(driving ?o4 ?o1)",
                "type": "Agent Dependency Constraint"
            }
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
            "intervention": {
                "action": "move",
                "omit_literal": "(clear ?o1)",
                "type": "Recursive Stack Clearance Invariant"
            }
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
            "intervention": {
                "action": "take-image",
                "omit_literal": "(calibrated ?o3)",
                "type": "Sensor Calibration State Lock"
            }
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
            "intervention": {
                "action": "navigate",
                "omit_literal": "(can-traverse ?o1 ?o2 ?o3)",
                "type": "Topological Traversability Bottleneck"
            }
        }
    }

def pilot_verify_bottlenecks() -> dict[str, Any]:
    print("\n==================================================================")
    print("2. PILOT BOTTLENECK PRECONDITION VERIFICATION ACROSS 8 IPC DOMAINS")
    print("==================================================================")

    configs = get_8domain_configs()
    verification_results = {}

    for domain_name, cfg in configs.items():
        with open(cfg["ref_file"], "r", encoding="utf-8") as f:
            ref_text = f.read()

        gt_models = parse_pddl_model(ref_text)
        objects = cfg["objects"]
        init = cfg["init"]
        goal = cfg["goal"]

        # 1. Verify Ground Truth M*
        gt_planner = GeneralForwardPlanner(gt_models, objects)
        gt_plan, _gt_nodes = gt_planner.solve(init, goal)
        gt_success, _gt_steps, _ = gt_planner.execute_plan(init, gt_plan, gt_models, goal)
        assert gt_success, f"Domain {domain_name} Ground Truth failed to solve or execute!"

        # 2. Apply Candidate Bottleneck Intervention
        int_cfg = cfg["intervention"]
        target_act = int_cfg["action"]
        omit_lit = int_cfg["omit_literal"].strip().lower()

        intervened_models = dict(gt_models)
        old_schema = gt_models[target_act]
        new_pre = [p for p in old_schema.preconditions if p.strip().lower() != omit_lit]
        raw_effects = old_schema.add_effects + [f"(not {d})" for d in old_schema.del_effects]
        intervened_models[target_act] = ActionSchema(
            old_schema.name, old_schema.params, new_pre, raw_effects
        )

        # 3. Solve on Intervened Model M_hat
        lrn_planner = GeneralForwardPlanner(intervened_models, objects)
        lrn_plan, _lrn_nodes = lrn_planner.solve(init, goal)

        # 4. Check for Phantom Edges and Real Execution Failure on M*
        phantom_count = 0
        if lrn_plan:
            sim_state = set(init)
            for act_name, args in lrn_plan:
                gt_schema = gt_models[act_name]
                pmap = {p: a for p, a in zip(gt_schema.params, args)}
                if not gt_schema.is_applicable(sim_state, pmap):
                    phantom_count += 1
                lrn_schema = intervened_models[act_name]
                lrn_pmap = {p: a for p, a in zip(lrn_schema.params, args)}
                sim_state = lrn_schema.apply(sim_state, lrn_pmap)

            exec_success, _steps, fail_reason = lrn_planner.execute_plan(
                init, lrn_plan, gt_models, goal
            )
            pesr = 1.0 if exec_success else 0.0
            r_play = str(max(0, len(lrn_plan) - len(gt_plan))) if exec_success else "INFINITY"
        else:
            exec_success, _steps, fail_reason = False, 0, "No plan found"
            pesr = 0.0
            r_play = "INFINITY"

        is_true_bottleneck = (not exec_success) and (phantom_count > 0)

        verification_results[domain_name] = {
            "bottleneck_precondition": omit_lit,
            "target_action": target_act,
            "constraint_archetype": int_cfg["type"],
            "gt_plan_length": len(gt_plan),
            "intervened_plan_length": len(lrn_plan) if lrn_plan else 0,
            "phantom_edges_detected": phantom_count,
            "PESR": pesr,
            "R_play": r_play,
            "execution_failure_reason": fail_reason,
            "is_verified_bottleneck": is_true_bottleneck
        }

        status = "PASSED (TRUE BOTTLENECK)" if is_true_bottleneck else "FAILED"
        print(f"[{status}] {domain_name:<12} | Action: {target_act:<12} | Omit: {omit_lit:<22} | Phantoms: {phantom_count} | PESR: {pesr} | R_play: {r_play}")

    return verification_results

if __name__ == "__main__":
    os.makedirs("benchmark_outputs", exist_ok=True)
    learner_data = benchmark_learners()
    bottleneck_data = pilot_verify_bottlenecks()

    pilot_report = {
        "learner_benchmark_compute": learner_data,
        "bottleneck_verification_8domains": bottleneck_data
    }

    out_file = "benchmark_outputs/pilot_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(pilot_report, f, indent=2)

    print(f"\nPilot results successfully written to {out_file}")
