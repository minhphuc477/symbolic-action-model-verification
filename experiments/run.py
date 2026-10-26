"""Unified, resumable experiment runner.

Usage::

    python -m experiments.run configs/pilot.yaml --workers 4

Each unit of work is one (domain, family, fault_seed). For that fault the runner records the
prior model's diagnostics (RQ1) and then runs every (feedback mode x method) pair (RQ2-RQ4).
Every record is appended as one JSON line to ``<out_dir>/records.jsonl``; finished units are
skipped on restart. ``<out_dir>/manifest.json`` stores git SHA, config, and environment.
"""

from __future__ import annotations

import argparse
import glob
import json
import platform
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from ammr.baselines import MonotonicRepairBaseline, RandomRepairBaseline, RandomSAMBaseline
from ammr.env import Environment, ObservationMode
from ammr.faults import FaultFamily, sample_faults
from ammr.metrics import (
    predictive_metrics,
    sample_reachable_states,
    solving_metrics,
    syntactic_metrics,
)
from ammr.pddl.io import load_domain, load_problem
from ammr.pddl.model import Domain, Problem, ground_universe, scramble_names
from ammr.planner import FastDownwardPlanner, Planner
from ammr.repair.loop import OnlineDomainRepair, RepairResult

BENCH = "external/AMLGym/amlgym/benchmarks"
FD_SEARCH = "lazy_greedy([ff()], preferred=[ff()])"


def load_benchmark(domain: str, n_learn: int, n_solve: int) -> tuple[Domain, list, list]:
    dom = load_domain(f"{BENCH}/domains/{domain}.pddl")
    learn = sorted(glob.glob(f"{BENCH}/problems/learning/{domain}/*.pddl"))[:n_learn]
    solve = sorted(glob.glob(f"{BENCH}/problems/solving/{domain}/*.pddl"))[:n_solve]
    return dom, [load_problem(p) for p in learn], [load_problem(p) for p in solve]


def _mode(spec: str) -> tuple[ObservationMode, float]:
    """Parse ``full`` | ``binary`` | ``partial:0.5``."""
    if spec.startswith("partial"):
        return ObservationMode.PARTIAL, float(spec.split(":")[1])
    return ObservationMode(spec), 1.0 if spec == "full" else 0.0


def run_method(
    method: str,
    prior: Domain,
    true_dom: Domain,
    learn: list[Problem],
    mode_spec: str,
    budget: int,
    seed: int,
    planner: Planner,
) -> RepairResult:
    mode, p_obs = _mode(mode_spec)

    def env_factory(prob: Problem, b: int) -> Environment:
        return Environment(true_dom, prob, mode=mode, obs_prob=p_obs, step_budget=b, seed=seed)

    if method in ("ours", "ours_coherence"):
        tie = "coherence" if method == "ours_coherence" else "lex"
        return OnlineDomainRepair(tie_break=tie).run(prior, learn, env_factory, planner, budget)
    if method == "monotonic":
        return MonotonicRepairBaseline().run(prior, learn, env_factory, planner, budget)
    if method == "random_repair":
        return RandomRepairBaseline(seed=seed).run(prior, learn, env_factory, budget)
    if method == "random_sam":
        return RandomSAMBaseline(seed=seed).run(prior, learn, env_factory, budget)
    raise ValueError(f"unknown method {method}")


def run_unit(unit: dict[str, Any], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Execute all (mode, method) runs for one fault. Never reads M* inside learners."""
    true_dom, learn, solve = load_benchmark(unit["domain"], cfg["n_learn"], cfg["n_solve"])
    if unit.get("scrambled"):
        orig, seed = true_dom, unit["fault_seed"]
        true_dom = scramble_names(orig, learn[0], seed)[0]
        learn = [scramble_names(orig, p, seed)[1] for p in learn]
        solve = [scramble_names(orig, p, seed)[1] for p in solve]
    faults = sample_faults(
        true_dom,
        FaultFamily(unit["family"]),
        count=1,
        k_edits=unit["k"],
        seed=unit["fault_seed"],
        problems=learn,
    )
    base = {k: unit[k] for k in ("domain", "family", "k", "fault_seed", "scrambled")}
    if not faults:
        return [{**base, "kind": "no_fault"}]
    prior, spec, impact = faults[0]
    timeout = cfg.get("planner_timeout_s", 20.0)
    records: list[dict[str, Any]] = []
    with FastDownwardPlanner(search=FD_SEARCH) as planner:
        states = sample_reachable_states(true_dom, learn, max_states=40, seed=unit["fault_seed"])
        ucache = {p.name: len(ground_universe(true_dom, p)) for p in learn}
        prior_rec = {
            **base,
            "kind": "prior",
            "edits": [asdict(e) for e in spec.edits],
            "init_impact": impact,
            "syntactic": asdict(syntactic_metrics(prior, true_dom)),
            "predictive": asdict(predictive_metrics(prior, true_dom, states, ucache)),
            "solving": asdict(solving_metrics(prior, true_dom, solve, planner, timeout)),
        }
        records.append(prior_rec)
        for mode_spec in cfg["modes"]:
            for budget in cfg["budgets"]:
                for method in cfg["methods"]:
                    ctx = {**base, "mode": mode_spec, "budget": budget, "method": method}
                    records.append(
                        _run_record(ctx, prior, true_dom, learn, solve, planner, timeout)
                    )
    return records


def _run_record(
    ctx: dict[str, Any],
    prior: Domain,
    true_dom: Domain,
    learn: list[Problem],
    solve: list[Problem],
    planner: Planner,
    timeout: float,
) -> dict[str, Any]:
    """Run one (mode, budget, method) and evaluate it on held-out problems."""
    t0 = time.perf_counter()
    try:
        res = run_method(
            ctx["method"],
            prior,
            true_dom,
            learn,
            ctx["mode"],
            ctx["budget"],
            ctx["fault_seed"],
            planner,
        )
    except Exception as exc:  # recorded, never silently dropped
        return {
            **ctx,
            "kind": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "trace": traceback.format_exc()[-1500:],
        }
    held_out = solving_metrics(res.repaired_domain, true_dom, solve, planner, timeout)
    return {
        **ctx,
        "kind": "run",
        "steps_used": res.steps_used,
        "episodes": res.episodes,
        "planner_calls": res.planner_calls,
        "relaxation_accepts": res.relaxation_accepts,
        "solved_training": list(res.solved_training),
        "syntactic": asdict(syntactic_metrics(res.repaired_domain, true_dom)),
        "solving": asdict(held_out),
        "wall_s": round(time.perf_counter() - t0, 2),
    }


def _unit_key(u: dict[str, Any]) -> str:
    return f"{u['domain']}|{u['family']}|{u['k']}|{u['fault_seed']}|{int(u['scrambled'])}"


def build_units(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    units = []
    for domain in cfg["domains"]:
        for family in cfg["families"]:
            k = 2 if family == "compound" else cfg.get("k", 1)
            for s in range(cfg["seeds"]):
                for scr in cfg.get("scrambled", [False]):
                    units.append(
                        {
                            "domain": domain,
                            "family": family,
                            "k": k,
                            "fault_seed": 1000 + s,
                            "scrambled": scr,
                        }
                    )
    return units


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _git_dirty() -> bool:
    out = subprocess.run(
        ["git", "status", "--porcelain", "ammr", "experiments"], capture_output=True, text=True
    ).stdout
    return bool(out.strip())


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out = Path(cfg["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    rec_path = out / "records.jsonl"
    done: set[str] = set()
    if rec_path.exists():
        for line in rec_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["kind"] in ("prior", "no_fault"):
                done.add(_unit_key(r))
    manifest = {
        "git_sha": _git_sha(),
        "git_dirty": _git_dirty(),
        "config": cfg,
        "python": sys.version,
        "platform": platform.platform(),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (out / f"manifest_{int(time.time())}.json").write_text(json.dumps(manifest, indent=2))
    todo = [u for u in build_units(cfg) if _unit_key(u) not in done]
    print(f"{len(done)} units done, {len(todo)} to run", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool, rec_path.open("a") as fh:
        futs = {pool.submit(run_unit, u, cfg): u for u in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            u = futs[fut]
            try:
                recs = fut.result()
            except Exception as exc:
                print(f"[{i}/{len(todo)}] FAILED {_unit_key(u)}: {exc}", flush=True)
                continue
            # prior/no_fault record written last so an interrupted unit is re-run whole
            recs.sort(key=lambda r: r["kind"] in ("prior", "no_fault"))
            for r in recs:
                fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(f"[{i}/{len(todo)}] {_unit_key(u)} ({len(recs)} records)", flush=True)


if __name__ == "__main__":
    main()
