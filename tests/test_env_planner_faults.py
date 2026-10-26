"""TDD unit and integration tests for ammr.env, ammr.planner, and ammr.faults."""

from __future__ import annotations

import pytest

from ammr.env import BudgetExhausted, Environment, ObservationMode
from ammr.faults import (
    FaultFamily,
    apply_fault,
    enumerate_single_edits,
    lifted_atom_candidates,
    sample_faults,
)
from ammr.pddl.io import load_domain, load_problem
from ammr.pddl.model import ground_universe
from ammr.planner import FastDownwardPlanner, PlanStatus, PythonBFSPlanner, validate_plan


def test_env_isolation_and_binary_feedback_leaks_zero_fluents() -> None:
    dom = load_domain("domains/blocksworld/domain.pddl")
    prob = load_problem("domains/blocksworld/problem_p01.pddl")
    env = Environment(dom, prob, mode=ObservationMode.BINARY, step_budget=10, seed=7)

    # True domain must not be publicly exposed
    assert not hasattr(env, "true_domain")
    assert not hasattr(env, "_true_domain")

    init_obs = env.reset()
    assert init_obs.pos == frozenset()
    assert init_obs.neg == frozenset()

    # Inapplicable action in s0: unstack b1 b2 when b1 is not on b2 (or check both outcomes)
    out = env.step(("stack", ("b1", "b2")))
    assert not out.applicable
    assert out.obs_before.pos == frozenset()
    assert out.obs_before.neg == frozenset()
    assert out.obs_after.pos == frozenset()
    assert out.obs_after.neg == frozenset()
    assert env.steps_used == 1


def test_env_partial_and_full_observability_properties() -> None:
    dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    univ = ground_universe(dom, prob)

    env_full = Environment(dom, prob, mode=ObservationMode.FULL, step_budget=10, seed=1)
    obs0 = env_full.reset()
    assert obs0.pos == prob.init
    assert obs0.pos | obs0.neg == univ
    assert obs0.pos.isdisjoint(obs0.neg)

    env_part = Environment(
        dom, prob, mode=ObservationMode.PARTIAL, obs_prob=0.5, step_budget=10, seed=42
    )
    p0 = env_part.reset()
    assert p0.pos <= prob.init
    assert p0.neg <= (univ - prob.init)
    assert 0 < len(p0.pos | p0.neg) < len(univ)


def test_env_budget_enforced() -> None:
    dom = load_domain("domains/gripper/domain.pddl")
    prob = load_problem("domains/gripper/problem_p01.pddl")
    env = Environment(dom, prob, mode=ObservationMode.BINARY, step_budget=2, seed=0)
    env.reset()
    env.step(("move", ("rooma", "roomb")))
    env.step(("move", ("roomb", "rooma")))
    with pytest.raises(BudgetExhausted):
        env.step(("move", ("rooma", "roomb")))


def test_python_and_fast_downward_planners_agree() -> None:
    dom = load_domain("domains/blocksworld/domain.pddl")
    prob = load_problem("domains/blocksworld/problem_p01.pddl")

    py_planner = PythonBFSPlanner()
    py_res = py_planner.solve(dom, prob, timeout_s=5.0)
    assert py_res.status == PlanStatus.SOLVED
    assert validate_plan(dom, prob, py_res.plan)

    with FastDownwardPlanner(search="astar(lmcut())") as fd_planner:
        fd_res = fd_planner.solve(dom, prob, timeout_s=15.0)
        assert fd_res.status == PlanStatus.SOLVED
        assert validate_plan(dom, prob, fd_res.plan)
        assert len(fd_res.plan) == len(py_res.plan)

        # Make goal unreachable by emptying all add effects
        broken = dom
        for act in dom.actions.values():
            broken = broken.with_action(act.with_changes(add=frozenset()))
        unsolv = fd_planner.solve(broken, prob, timeout_s=10.0)
        assert unsolv.status == PlanStatus.UNSOLVABLE


def test_fault_generator_covers_all_families_reproducibly() -> None:
    dom = load_domain("domains/barman/domain.pddl")
    prob = load_problem("domains/barman/problem_p01.pddl")

    for act in dom.actions.values():
        cands = set(lifted_atom_candidates(dom, act))
        assert act.pre_pos <= cands
        assert act.add <= cands
        assert act.delete <= cands

    for fam in (
        FaultFamily.MISSING_PREC,
        FaultFamily.SPURIOUS_PREC,
        FaultFamily.CORRUPT_EFFECT,
    ):
        edits = enumerate_single_edits(dom, fam)
        assert len(edits) > 0

    s1 = sample_faults(dom, FaultFamily.COMPOUND, count=4, k_edits=2, seed=123, problems=[prob])
    s2 = sample_faults(dom, FaultFamily.COMPOUND, count=4, k_edits=2, seed=123, problems=[prob])
    assert [f for _, f, _ in s1] == [f for _, f, _ in s2]
    for mutated, spec, _ in s1:
        assert mutated != dom
        assert apply_fault(dom, spec) == mutated
