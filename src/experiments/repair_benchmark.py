"""
repair_benchmark.py
===================
YAML-driven empirical benchmark for Bidirectional and Compound Action Model Repair.
Evaluates CEG-OMR against:
  1. Monotonic-Only CEG-OMR / OLAM-style online refinement
  2. Active SAM (Goal-directed Safe Action Model Learning)
  3. Passive SAM (M = 250 random exploratory transitions)

Driven by:
  - configs/experiments/repair_benchmark.yaml
  - configs/interventions/bidirectional_suite.yaml
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

# Ensure repo root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.repair import CEGOMRConfig, CEGOMREngine, SAMBaseline
from src.utils.sexp import (
    _find_action_block,
    _get_section,
    _parse_sexp,
    _sexp_to_str,
    _tokenize,
)


def _mutate_domain_sexp(domain_path: str, mutator_fn, out_path: Path) -> str:
    text = Path(domain_path).read_text(encoding="utf-8")
    tokens = _tokenize(text)
    sexp, _ = _parse_sexp(tokens)
    sexp_copy = copy.deepcopy(sexp)
    mutator_fn(sexp_copy)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_sexp_to_str(sexp_copy) + "\n", encoding="utf-8")
    return str(out_path)


def _remove_precondition_atom(sexp: list, action_name: str, target_norm: str) -> None:
    act = _find_action_block(sexp, action_name)
    if act is None:
        raise ValueError(f"Action {action_name} not found")
    idx = _get_section(act, ":precondition")
    prec = act[idx + 1]
    prec[1:] = [c for c in prec[1:] if _sexp_to_str(c).strip().lower() != target_norm.lower()]


def _add_precondition_atom(sexp: list, action_name: str, atom_str: str) -> None:
    act = _find_action_block(sexp, action_name)
    if act is None:
        raise ValueError(f"Action {action_name} not found")
    idx = _get_section(act, ":precondition")
    prec = act[idx + 1]
    atom_sexp, _ = _parse_sexp(_tokenize(atom_str))
    if isinstance(prec, list) and prec and prec[0].lower() == "and":
        prec.append(atom_sexp)
    else:
        act[idx + 1] = ["and", prec, atom_sexp]


def _remove_effect_atom(sexp: list, action_name: str, target_norm: str) -> None:
    act = _find_action_block(sexp, action_name)
    if act is None:
        raise ValueError(f"Action {action_name} not found")
    idx = _get_section(act, ":effect")
    eff = act[idx + 1]
    eff[1:] = [c for c in eff[1:] if _sexp_to_str(c).strip().lower() != target_norm.lower()]


def _add_effect_atom(sexp: list, action_name: str, atom_str: str) -> None:
    act = _find_action_block(sexp, action_name)
    if act is None:
        raise ValueError(f"Action {action_name} not found")
    idx = _get_section(act, ":effect")
    eff = act[idx + 1]
    atom_sexp, _ = _parse_sexp(_tokenize(atom_str))
    if isinstance(eff, list) and eff and eff[0].lower() == "and":
        eff.append(atom_sexp)
    else:
        act[idx + 1] = ["and", eff, atom_sexp]


def apply_mutation_spec(sexp: list, mutation: dict[str, str]) -> None:
    m_type = mutation["type"]
    act = mutation["action"]
    atom = mutation["atom"]
    if m_type == "remove_precondition":
        _remove_precondition_atom(sexp, act, atom)
    elif m_type == "add_precondition":
        _add_precondition_atom(sexp, act, atom)
    elif m_type == "remove_effect":
        _remove_effect_atom(sexp, act, atom)
    elif m_type == "add_effect":
        _add_effect_atom(sexp, act, atom)
    else:
        raise ValueError(f"Unknown mutation type: {m_type}")


def build_fault_scenarios_from_yaml(
    base_out_dir: Path,
    config_path: str = "configs/interventions/bidirectional_suite.yaml",
) -> list[dict[str, Any]]:
    cfg_p = Path(config_path)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_path
    data = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))

    scenarios = []
    for family_name, scen_list in data["families"].items():
        for scen in scen_list:
            scen_id = scen["scenario_id"]
            gt_dom = scen["gt_domain"]
            mutations = scen.get("mutations", [])

            def mut_fn(sexp, muts=mutations):
                for m in muts:
                    apply_mutation_spec(sexp, m)

            mut_path = _mutate_domain_sexp(
                gt_dom, mut_fn, base_out_dir / f"{scen_id}.pddl"
            )
            missing_atom = ""
            if mutations and mutations[0]["type"] == "remove_precondition":
                missing_atom = mutations[0]["atom"]

            scenarios.append({
                "family": family_name,
                "scenario_id": scen_id,
                "domain": scen["domain"],
                "gt_domain": gt_dom,
                "mutated_domain": mut_path,
                "problem": scen["problem"],
                "target_action": scen["target_action"],
                "missing_atom": missing_atom,
                "description": scen["description"],
            })
    return scenarios


def run_monotonic_olam_style_baseline(
    mutated_domain: str,
    gt_domain: str,
    problem: str,
    out_dir: Path,
    seed: int,
) -> dict[str, Any]:
    cfg = CEGOMRConfig(
        domain_path=mutated_domain,
        problem_path=problem,
        ground_truth_domain=gt_domain,
        out_dir=str(out_dir),
        max_repair_iterations=15,
        max_environment_steps=100,
        enable_backtracking=False,
        use_effect_coherence=False,
        allow_relaxation=False,
        allow_effect_deletion=False,
        seed=seed,
    )
    engine = CEGOMREngine(cfg)
    res = engine.run()
    return {
        "success": res.success,
        "total_queries": res.total_queries,
        "iterations": res.iterations,
        "wall_clock_seconds": round(res.wall_clock_seconds, 3),
    }


def run_repair_benchmark(
    config_file: str = "configs/experiments/repair_benchmark.yaml",
) -> dict[str, Any]:
    cfg_p = Path(config_file)
    if not cfg_p.exists():
        cfg_p = Path(__file__).resolve().parent.parent.parent / config_file
    exp_cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))

    suite_cfg = exp_cfg.get("suite_config", "configs/interventions/bidirectional_suite.yaml")
    seeds = exp_cfg.get("seeds", [42, 123, 999])
    out_file = Path(exp_cfg.get("output_file", "benchmark_outputs/bidirectional_and_compound_repair_benchmark.json"))

    base_mut_dir = Path("domains/mutated/bidirectional_bench")
    scenarios = build_fault_scenarios_from_yaml(base_mut_dir, suite_cfg)

    print("=" * 80)
    print(f"RUNNING BIDIRECTIONAL REPAIR BENCHMARK: {len(scenarios)} scenarios x {len(seeds)} seeds = {len(scenarios) * len(seeds)} runs")
    print(f"Config: {config_file}")
    print("=" * 80)

    rows: list[dict[str, Any]] = []

    for scen in scenarios:
        scen_id = scen["scenario_id"]
        fam = scen["family"]
        dom_id = scen["domain"]
        gt_dom = scen["gt_domain"]
        mut_dom = scen["mutated_domain"]
        prob = scen["problem"]
        t_act = scen["target_action"]
        m_atom = scen["missing_atom"]

        for seed in seeds:
            # 1. CEG-OMR (Proposed)
            ceg_dir = Path(f"repair_logs/bench_ceg/{scen_id}_s{seed}")
            ceg_cfg = CEGOMRConfig(
                domain_path=mut_dom,
                problem_path=prob,
                ground_truth_domain=gt_dom,
                out_dir=str(ceg_dir),
                max_repair_iterations=15,
                max_environment_steps=100,
                enable_backtracking=True,
                use_effect_coherence=True,
            )
            engine = CEGOMREngine(ceg_cfg)
            res_ceg = engine.repair()

            # 2. Monotonic-OLAM style baseline
            mono_dir = Path(f"repair_logs/bench_mono/{scen_id}_s{seed}")
            res_mono = run_monotonic_olam_style_baseline(mut_dom, gt_dom, prob, mono_dir, seed=seed)

            # 3. Active SAM baseline
            asam_dir = Path(f"repair_logs/bench_asam/{scen_id}_s{seed}")
            sam_active = SAMBaseline(seed=seed)
            res_asam = sam_active.run_active_sam(
                domain_path=mut_dom,
                problem_path=prob,
                gt_domain_path=gt_dom,
                max_iterations=15,
                out_dir=str(asam_dir),
            )

            # 4. Passive SAM baseline (M=250)
            psam_dir = Path(f"repair_logs/bench_psam/{scen_id}_s{seed}")
            sam_passive = SAMBaseline(seed=seed)
            psam_dict = sam_passive.run_passive_sam(
                domain_path=mut_dom,
                problem_path=prob,
                gt_domain_path=gt_dom,
                sample_budgets=[250],
                target_action=t_act,
                missing_atom=m_atom,
                out_dir=str(psam_dir),
            )
            res_psam = psam_dict[250]

            row = {
                "family": fam,
                "scenario_id": scen_id,
                "domain": dom_id,
                "seed": seed,
                "description": scen["description"],
                "ceg_omr_bidirectional": {
                    "success": res_ceg.success,
                    "queries": res_ceg.total_queries,
                    "iterations": res_ceg.iterations,
                    "time_s": round(res_ceg.wall_clock_seconds, 3),
                },
                "monotonic_olam_style": {
                    "success": res_mono["success"],
                    "queries": res_mono["total_queries"],
                    "iterations": res_mono["iterations"],
                    "time_s": res_mono["wall_clock_seconds"],
                },
                "active_sam": {
                    "success": res_asam.success,
                    "queries": res_asam.total_samples,
                    "time_s": round(res_asam.wall_clock_seconds, 3),
                },
                "passive_sam_250": {
                    "success": res_psam.success,
                    "queries": res_psam.total_samples,
                    "time_s": round(res_psam.wall_clock_seconds, 3),
                },
            }
            rows.append(row)
            print(
                f"  [{scen_id} | seed={seed}] "
                f"CEG-OMR={row['ceg_omr_bidirectional']['success']} (K={row['ceg_omr_bidirectional']['queries']}), "
                f"Mono={row['monotonic_olam_style']['success']}, "
                f"ActiveSAM={row['active_sam']['success']}, "
                f"PassiveSAM250={row['passive_sam_250']['success']}"
            )

    # Aggregate by family and overall
    summary_by_family: dict[str, Any] = {}
    families = sorted(set(r["family"] for r in rows))
    methods = ["ceg_omr_bidirectional", "monotonic_olam_style", "active_sam", "passive_sam_250"]

    for fam in families:
        fam_rows = [r for r in rows if r["family"] == fam]
        fam_stats: dict[str, Any] = {"n_runs": len(fam_rows)}
        for m in methods:
            succs = [1 if r[m]["success"] else 0 for r in fam_rows]
            qs = [r[m]["queries"] for r in fam_rows]
            succ_qs = [r[m]["queries"] for r in fam_rows if r[m]["success"]]
            fam_stats[m] = {
                "solve_rate_pct": round(100.0 * float(np.mean(succs)), 2),
                "mean_queries_all": round(float(np.mean(qs)), 2),
                "std_queries_all": round(float(np.std(qs)), 2),
                "mean_queries_when_solved": round(float(np.mean(succ_qs)), 2) if succ_qs else None,
            }
        summary_by_family[fam] = fam_stats

    overall_stats: dict[str, Any] = {"n_runs": len(rows)}
    for m in methods:
        succs = [1 if r[m]["success"] else 0 for r in rows]
        qs = [r[m]["queries"] for r in rows]
        succ_qs = [r[m]["queries"] for r in rows if r[m]["success"]]
        overall_stats[m] = {
            "solve_rate_pct": round(100.0 * float(np.mean(succs)), 2),
            "mean_queries_all": round(float(np.mean(qs)), 2),
            "std_queries_all": round(float(np.std(qs)), 2),
            "mean_queries_when_solved": round(float(np.mean(succ_qs)), 2) if succ_qs else None,
        }

    out_payload = {
        "n_scenarios": len(scenarios),
        "n_seeds": len(seeds),
        "total_runs_per_method": len(rows),
        "overall": overall_stats,
        "by_family": summary_by_family,
        "rows": rows,
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(out_payload, indent=2), encoding="utf-8")
    print(f"\n[Bidirectional Benchmark] Saved results to {out_file}")
    return out_payload


if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else "configs/experiments/repair_benchmark.yaml"
    run_repair_benchmark(cfg_file)
