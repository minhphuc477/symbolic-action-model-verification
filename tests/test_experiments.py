"""Tests for experiments.analyze and experiments.claim_audit (no planner needed)."""

from __future__ import annotations

import pytest

from experiments.analyze import bootstrap_ci, summarize
from experiments.claim_audit import resolve


def _prior(seed: int, acc: float, sol: float) -> dict:
    return {
        "kind": "prior",
        "domain": "d",
        "family": "f",
        "k": 1,
        "fault_seed": seed,
        "scrambled": False,
        "predictive": {"transition_accuracy": acc},
        "solving": {"solving_ratio": sol},
    }


def _run(seed: int, method: str, sol: float) -> dict:
    return {
        "kind": "run",
        "domain": "d",
        "family": "f",
        "k": 1,
        "fault_seed": seed,
        "scrambled": False,
        "mode": "full",
        "budget": 50,
        "method": method,
        "steps_used": 10,
        "solving": {"solving_ratio": sol, "false_plans_ratio": 0.0},
        "syntactic": {"f1": 1.0, "edit_distance": 0},
    }


def test_bootstrap_ci_brackets_mean() -> None:
    lo, hi = bootstrap_ci([0.0, 1.0] * 20)
    assert lo <= 0.5 <= hi


def test_summarize_excludes_silent_faults_and_pairs_methods() -> None:
    recs = [_prior(0, 0.99, 0.0), _prior(1, 0.97, 1.0)]  # fault 1 is silent
    recs += [_run(0, "ours", 1.0), _run(0, "monotonic", 0.0)]
    recs += [_run(1, "ours", 0.0), _run(1, "monotonic", 1.0)]  # must be ignored
    s = summarize(recs)
    assert s["n_faults"] == 2 and s["n_impactful"] == 1
    assert s["rq1"]["n_acc_ge_095_and_solving_0"] == 1
    assert not s["rq1"]["h1_falsified"]
    t = s["paired"][0]
    assert (t["other"], t["wins"], t["losses"], t["n_pairs"]) == ("monotonic", 1, 0, 1)


def test_claim_selector_resolution() -> None:
    data = {"cells": [{"mode": "full", "budget": 50, "v": 0.5}, {"mode": "binary", "v": 0.1}]}
    assert resolve(data, "cells[mode=full,budget=50].v") == 0.5
    assert resolve(data, "cells.1.v") == 0.1
    with pytest.raises(KeyError):
        resolve(data, "cells[mode=partial].v")
