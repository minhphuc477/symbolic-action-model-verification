"""Unit tests for ammr.baselines and ammr.metrics."""

from __future__ import annotations

from ammr.baselines import (
    MonotonicRepairBaseline,
    RandomRepairBaseline,
    RandomSAMBaseline,
)
from ammr.env import Environment, ObservationMode
from ammr.faults import AtomicEdit, FaultFamily, apply_edit, enumerate_single_edits
from ammr.metrics import (
    predictive_metrics,
    sample_reachable_states,
    solving_metrics,
    syntactic_metrics,
)
from ammr.pddl.io import load_domain, load_problem
from ammr.pddl.model import ground_universe
from ammr.planner import PythonBFSPlanner


def test_metrics_identity_and_degradation() -> None:
    dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    planner = PythonBFSPlanner()

    syn_ok = syntactic_metrics(dom, dom)
    assert syn_ok.f1 == 1.0
    assert syn_ok.edit_distance == 0

    states = sample_reachable_states(dom, [prob], max_states=15, seed=0)
    ucache = {prob.name: len(ground_universe(dom, prob))}
    pred_ok = predictive_metrics(dom, dom, states, ucache)
    assert pred_ok.applicability_precision == 1.0
    assert pred_ok.effects_precision == 1.0
    assert pred_ok.transition_accuracy == 1.0
    assert pred_ok.fluent_accuracy == 1.0

    solv_ok = solving_metrics(dom, dom, [prob], planner)
    assert solv_ok.solving_ratio == 1.0
    assert solv_ok.false_plans_ratio == 0.0

    # Mutate drop by removing (at ?obj ?room) add effect -> 1 edit, solving_ratio drops to 0
    at_atom = next(a for a in dom.actions["drop"].add if a[0] == "at")
    bad = apply_edit(dom, AtomicEdit("drop", "rem_add", at_atom))
    syn_bad = syntactic_metrics(bad, dom)
    assert syn_bad.edit_distance == 1
    assert syn_bad.f1 < 1.0
    solv_bad = solving_metrics(bad, dom, [prob], planner)
    assert solv_bad.solving_ratio == 0.0
    assert solv_bad.unsolvable_ratio == 1.0


def test_sam_baseline_safety_guarantee() -> None:
    """Under FULL observability, SAM's learned model never emits false plans (false_plans == 0)."""
    dom = load_domain("domains/gripper/domain.pddl")
    p1 = load_problem("domains/gripper/problem_p01.pddl")
    p2 = load_problem("domains/gripper/problem_p02.pddl")
    planner = PythonBFSPlanner()

    for budget in (15, 60, 150):
        sam = RandomSAMBaseline(seed=42, episode_len=20)
        res = sam.run(
            dom,
            [p1],
            lambda prob, b: Environment(dom, prob, ObservationMode.FULL, step_budget=b, seed=42),
            total_step_budget=budget,
        )
        assert res.steps_used <= budget
        solv = solving_metrics(res.repaired_domain, dom, [p1, p2], planner)
        assert solv.false_plans_ratio == 0.0


def test_random_repair_and_monotonic_baselines() -> None:
    dom = load_domain("domains/blocksworld/domain.pddl")
    p1 = load_problem("domains/blocksworld/problem_p01.pddl")
    p2 = load_problem("domains/blocksworld/problem_p02.pddl")
    planner = PythonBFSPlanner()

    miss = next(iter(enumerate_single_edits(dom, FaultFamily.MISSING_PREC)))
    prior_miss = apply_edit(dom, miss)

    mono = MonotonicRepairBaseline()
    res_mono = mono.run(
        prior_miss,
        [p1],
        lambda prob, b: Environment(dom, prob, ObservationMode.FULL, step_budget=b, seed=1),
        planner,
        total_step_budget=80,
    )
    assert res_mono.solved_training == (True,)

    # Monotonic baseline genuinely fails on an unsolvable spurious precondition
    spur = next(
        e for e in enumerate_single_edits(dom, FaultFamily.SPURIOUS_PREC) if "pick" in e.action
    )
    prior_spur = apply_edit(dom, spur)
    res_mono_spur = mono.run(
        prior_spur,
        [p1, p2],
        lambda prob, b: Environment(dom, prob, ObservationMode.FULL, step_budget=b, seed=1),
        planner,
        total_step_budget=80,
    )
    assert res_mono_spur.relaxation_accepts == 0

    rand_rep = RandomRepairBaseline(seed=7)
    res_rand = rand_rep.run(
        prior_miss,
        [p1],
        lambda prob, b: Environment(dom, prob, ObservationMode.FULL, step_budget=b, seed=7),
        total_step_budget=80,
    )
    assert res_rand.steps_used == 80
