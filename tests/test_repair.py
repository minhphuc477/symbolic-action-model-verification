"""Unit and property tests for ammr.repair (hypotheses, update, closed-loop repair)."""

from __future__ import annotations

import random

import pytest

from ammr.env import Environment, ObservationMode
from ammr.faults import AtomicEdit, apply_edit
from ammr.pddl.io import load_domain, load_problem
from ammr.pddl.model import ground_actions
from ammr.planner import PythonBFSPlanner, validate_plan
from ammr.repair.hypotheses import DomainVersionSpace
from ammr.repair.loop import OnlineDomainRepair
from ammr.repair.update import solve_min_hitting_sets


def test_min_hitting_set_exactness() -> None:
    c1 = frozenset({(True, ("a",)), (True, ("b",))})
    c2 = frozenset({(True, ("b",)), (True, ("c",))})
    sols = solve_min_hitting_sets([c1, c2])
    assert sols == [frozenset({(True, ("b",))})]

    # Disjoint clauses require cardinality 2; contradictory literals on same atom excluded
    d1 = frozenset({(True, ("p",))})
    d2 = frozenset({(False, ("p",)), (True, ("q",))})
    sols2 = solve_min_hitting_sets([d1, d2])
    assert sols2 == [frozenset({(True, ("p",)), (True, ("q",))})]


@pytest.mark.parametrize("obs_prob", [1.0, 0.8, 0.5, 0.2])
def test_version_space_soundness_under_partial_and_noninjective_calls(obs_prob: float) -> None:
    """Proposition 1: M* remains inside V(D) for all sensor masks and non-injective bindings."""
    dom = load_domain("domains/blocksworld/domain.pddl")
    prob = load_problem("domains/blocksworld/problem_p01.pddl")
    mode = ObservationMode.FULL if obs_prob == 1.0 else ObservationMode.PARTIAL
    env = Environment(dom, prob, mode=mode, obs_prob=obs_prob, step_budget=80, seed=17)
    vspace = DomainVersionSpace(dom)
    all_ops = list(ground_actions(dom, prob))
    rng = random.Random(99)

    env.reset()
    for _ in range(60):
        ga = rng.choice(all_ops)  # includes non-injective ('stack', ('b1', 'b1'))
        out = env.step(ga)
        vspace.observe_step(out)
        assert vspace.is_domain_consistent(dom)


@pytest.mark.parametrize(
    ("mode", "prob_val"),
    [
        (ObservationMode.FULL, 1.0),
        (ObservationMode.PARTIAL, 0.5),
        (ObservationMode.BINARY, 0.0),
    ],
)
def test_repair_missing_precondition_across_feedback_modes(
    mode: ObservationMode, prob_val: float
) -> None:
    true_dom = load_domain("domains/blocksworld/domain.pddl")
    train_prob = load_problem("domains/blocksworld/problem_p01.pddl")
    test_prob = load_problem("domains/blocksworld/problem_p02.pddl")

    # Drop (ontable ?x) from pick-up (or check exact action name in local domain)
    pick_name = next(n for n in true_dom.actions if "pick" in n)
    ontable_atom = next(a for a in true_dom.actions[pick_name].pre_pos if "ontable" in a[0])
    prior = apply_edit(true_dom, AtomicEdit(pick_name, "rem_pre_pos", ontable_atom))

    planner = PythonBFSPlanner()
    agent = OnlineDomainRepair(tie_break="lex")
    env = Environment(true_dom, train_prob, mode=mode, obs_prob=prob_val, step_budget=80, seed=7)
    res = agent.repair_single(prior, train_prob, env, planner)

    assert res.solved_training == (True,)
    test_plan = planner.solve(res.repaired_domain, test_prob)
    assert validate_plan(true_dom, test_prob, test_plan.plan)


def test_repair_negative_precondition_in_dungeon_escape() -> None:
    true_dom = load_domain("domains/dungeon_escape/domain.pddl")
    prob = load_problem("domains/dungeon_escape/problem_p01.pddl")
    locked_atom = next(iter(true_dom.actions["move"].pre_neg))
    prior = apply_edit(true_dom, AtomicEdit("move", "rem_pre_neg", locked_atom))

    planner = PythonBFSPlanner()
    env = Environment(true_dom, prob, mode=ObservationMode.FULL, step_budget=80, seed=3)
    res = OnlineDomainRepair().repair_single(prior, prob, env, planner)
    assert res.solved_training == (True,)
    check = planner.solve(res.repaired_domain, prob)
    assert validate_plan(true_dom, prob, check.plan)


def test_repair_spurious_precondition_via_planner_relaxation() -> None:
    true_dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    from ammr.faults import FaultFamily, enumerate_single_edits

    spurious_edit = next(
        e for e in enumerate_single_edits(true_dom, FaultFamily.SPURIOUS_PREC) if e.action == "pick"
    )
    prior = apply_edit(true_dom, spurious_edit)

    planner = PythonBFSPlanner()
    env = Environment(true_dom, prob, mode=ObservationMode.FULL, step_budget=80, seed=5)
    res = OnlineDomainRepair().repair_single(prior, prob, env, planner)
    assert res.solved_training == (True,)
    assert res.relaxation_accepts >= 1
    check = planner.solve(res.repaired_domain, prob)
    assert validate_plan(true_dom, prob, check.plan)


def test_repair_corrupt_effects_missing_add_and_spurious_del() -> None:
    true_dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    planner = PythonBFSPlanner()

    # 1. Missing add effect on drop (makes goal unreachable -> relaxation + confirmation)
    at_atom = next(a for a in true_dom.actions["drop"].add if a[0] == "at")
    prior_miss_add = apply_edit(true_dom, AtomicEdit("drop", "rem_add", at_atom))
    env1 = Environment(true_dom, prob, mode=ObservationMode.FULL, step_budget=80, seed=11)
    res1 = OnlineDomainRepair().repair_single(prior_miss_add, prob, env1, planner)
    assert res1.solved_training == (True,)
    assert validate_plan(true_dom, prob, planner.solve(res1.repaired_domain, prob).plan)

    # 2. Spurious delete effect on drop (deletes at-robby when dropping a ball)
    drop_act = true_dom.actions["drop"]
    from ammr.faults import lifted_atom_candidates

    extra_del = next(
        c
        for c in lifted_atom_candidates(true_dom, drop_act)
        if c not in drop_act.add | drop_act.delete
    )
    prior_spur_del = apply_edit(true_dom, AtomicEdit("drop", "add_del", extra_del))
    env2 = Environment(true_dom, prob, mode=ObservationMode.FULL, step_budget=80, seed=12)
    res2 = OnlineDomainRepair().repair_single(prior_spur_del, prob, env2, planner)
    assert res2.solved_training == (True,)
    assert validate_plan(true_dom, prob, planner.solve(res2.repaired_domain, prob).plan)


def test_repair_compound_two_fault_domain() -> None:
    true_dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    from ammr.faults import FaultFamily, enumerate_single_edits

    miss_pre = next(
        e for e in enumerate_single_edits(true_dom, FaultFamily.MISSING_PREC) if e.action == "pick"
    )
    spur_pre = next(
        e for e in enumerate_single_edits(true_dom, FaultFamily.SPURIOUS_PREC) if e.action == "drop"
    )
    prior = apply_edit(apply_edit(true_dom, miss_pre), spur_pre)

    planner = PythonBFSPlanner()
    env = Environment(true_dom, prob, mode=ObservationMode.FULL, step_budget=100, seed=19)
    res = OnlineDomainRepair().repair_single(prior, prob, env, planner)
    assert res.solved_training == (True,)
    assert validate_plan(true_dom, prob, planner.solve(res.repaired_domain, prob).plan)
