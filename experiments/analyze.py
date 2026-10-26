"""Statistical summary of ``records.jsonl``: means, bootstrap CIs, paired Wilcoxon tests.

Usage::

    python -m experiments.analyze results/main

Writes ``summary.json`` and ``summary.md`` next to the records. Main tables use *impactful*
faults only (the faulty prior fails at least one held-out problem); silent faults are counted
and reported. Every number in the thesis must come from these files.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from scipy.stats import spearmanr, wilcoxon

BOOT = 2000
Rec = dict[str, Any]


def bootstrap_ci(xs: list[float], seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap 95 % CI of the mean."""
    if not xs:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    vals = sorted(mean(rng.choice(xs) for _ in xs) for _ in range(BOOT))
    return (vals[int(0.025 * BOOT)], vals[int(0.975 * BOOT) - 1])


def load(path: Path) -> list[Rec]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def fault_key(r: Rec) -> tuple:
    return (r["domain"], r["family"], r["k"], r["fault_seed"], r["scrambled"])


def rq1(priors: list[Rec]) -> Rec:
    """Prediction accuracy of the faulty prior vs. its held-out solving ratio (H1)."""
    acc = [p["predictive"]["transition_accuracy"] for p in priors]
    sol = [p["solving"]["solving_ratio"] for p in priors]
    rho, pval = (None, None)
    if len(set(acc)) > 1 and len(set(sol)) > 1:
        res = spearmanr(acc, sol)
        rho, pval = float(res.statistic), float(res.pvalue)
    high = [p for p in priors if p["predictive"]["transition_accuracy"] >= 0.95]
    return {
        "n_faults": len(priors),
        "spearman_rho": rho,
        "spearman_p": pval,
        "n_acc_ge_095": len(high),
        "n_acc_ge_095_and_solving_0": sum(p["solving"]["solving_ratio"] == 0 for p in high),
        "n_acc_ge_095_and_solving_lt_09": sum(p["solving"]["solving_ratio"] < 0.9 for p in high),
        "h1_falsified": bool(high) and all(p["solving"]["solving_ratio"] >= 0.9 for p in high),
    }


def per_cell(runs: list[Rec], keys: tuple[str, ...]) -> list[Rec]:
    cells: dict[tuple, list[Rec]] = defaultdict(list)
    for r in runs:
        cells[tuple(r[k] for k in keys)].append(r)
    rows = []
    for cell, rs in sorted(cells.items(), key=lambda kv: tuple(map(str, kv[0]))):
        sol = [r["solving"]["solving_ratio"] for r in rs]
        lo, hi = bootstrap_ci(sol)
        rows.append(
            {
                **dict(zip(keys, cell)),
                "n": len(rs),
                "solving_mean": mean(sol),
                "solving_ci95": [lo, hi],
                "false_plans_mean": mean(r["solving"]["false_plans_ratio"] for r in rs),
                "f1_mean": mean(r["syntactic"]["f1"] for r in rs),
                "exact_recovery": mean(r["syntactic"]["edit_distance"] == 0 for r in rs),
                "steps_median": median(float(r["steps_used"]) for r in rs),
            }
        )
    return rows


def paired_tests(runs: list[Rec], ref: str = "ours") -> list[Rec]:
    """Paired Wilcoxon on held-out solving ratio, ``ref`` vs each method per (mode, budget)."""
    by: dict[tuple, dict[str, float]] = defaultdict(dict)
    for r in runs:
        by[(r["mode"], r["budget"], fault_key(r))][r["method"]] = r["solving"]["solving_ratio"]
    out = []
    for mode, budget in sorted({(m, b) for m, b, _ in by}):
        for other in sorted({r["method"] for r in runs} - {ref}):
            diffs = [
                v[ref] - v[other]
                for (m, b, _), v in by.items()
                if m == mode and b == budget and ref in v and other in v
            ]
            nz = [d for d in diffs if d != 0]
            lo, hi = bootstrap_ci(diffs) if diffs else (None, None)
            out.append(
                {
                    "mode": mode,
                    "budget": budget,
                    "other": other,
                    "n_pairs": len(diffs),
                    "mean_diff": mean(diffs) if diffs else None,
                    "diff_ci95": [lo, hi],
                    "wins": sum(d > 0 for d in diffs),
                    "losses": sum(d < 0 for d in diffs),
                    "ties": sum(d == 0 for d in diffs),
                    "wilcoxon_p": float(wilcoxon(nz).pvalue) if len(nz) >= 6 else None,
                }
            )
    return out


def summarize(records: list[Rec]) -> Rec:
    priors = [r for r in records if r["kind"] == "prior"]
    impactful = {fault_key(p) for p in priors if p["solving"]["solving_ratio"] < 1.0}
    runs = [r for r in records if r["kind"] == "run" and fault_key(r) in impactful]
    return {
        "rq1": rq1(priors),
        "n_faults": len(priors),
        "n_impactful": len(impactful),
        "cells_overall": per_cell(runs, ("mode", "budget", "method")),
        "cells_family": per_cell(runs, ("mode", "budget", "family", "method")),
        "paired": paired_tests(runs),
        "n_errors": sum(r["kind"] == "error" for r in records),
        "n_no_fault": sum(r["kind"] == "no_fault" for r in records),
    }


def _fmt(x: float | None, spec: str) -> str:
    return "n/a" if x is None else format(x, spec)


def _cell_table(rows: list[Rec], keys: tuple[str, ...]) -> list[str]:
    head = list(keys) + ["n", "solving [95% CI]", "false plans", "F1", "exact", "steps (med)"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for c in rows:
        lo, hi = c["solving_ci95"]
        vals = [str(c[k]) for k in keys] + [
            str(c["n"]),
            f"{c['solving_mean']:.3f} [{lo:.3f}, {hi:.3f}]",
            f"{c['false_plans_mean']:.3f}",
            f"{c['f1_mean']:.3f}",
            f"{c['exact_recovery']:.2f}",
            f"{c['steps_median']:.0f}",
        ]
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def to_markdown(s: Rec) -> str:
    lines = ["# Experiment summary (auto-generated by experiments.analyze; do not edit)", ""]
    lines += [
        f"Faults sampled: {s['n_faults']}; impactful (prior solving ratio < 1): "
        f"{s['n_impactful']}; silent: {s['n_faults'] - s['n_impactful']}. "
        f"Errors: {s['n_errors']}; units without a valid fault: {s['n_no_fault']}.",
        "",
        "## RQ1: faulty-prior transition accuracy vs. held-out plan success (all faults)",
        "",
    ]
    lines += [f"- {k}: {v}" for k, v in s["rq1"].items()]
    lines += ["", "## Held-out solving on impactful faults (pooled over families)", ""]
    lines += _cell_table(s["cells_overall"], ("mode", "budget", "method"))
    lines += ["", "## Per fault family", ""]
    lines += _cell_table(s["cells_family"], ("mode", "budget", "family", "method"))
    lines += [
        "",
        "## Paired comparisons (held-out solving ratio, ours minus other)",
        "",
        "| mode | budget | other | n | mean diff [95% CI] | W/L/T | Wilcoxon p |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in s["paired"]:
        lo, hi = t["diff_ci95"]
        md = "n/a" if t["mean_diff"] is None else f"{t['mean_diff']:+.3f} [{lo:+.3f}, {hi:+.3f}]"
        lines.append(
            f"| {t['mode']} | {t['budget']} | {t['other']} | {t['n_pairs']} | {md} | "
            f"{t['wins']}/{t['losses']}/{t['ties']} | {_fmt(t['wilcoxon_p'], '.2g')} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    args = ap.parse_args(argv)
    out = Path(args.out_dir)
    summary = summarize(load(out / "records.jsonl"))
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "summary.md").write_text(to_markdown(summary), encoding="utf-8")
    print(to_markdown(summary))


if __name__ == "__main__":
    main()
