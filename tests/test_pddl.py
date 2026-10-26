"""Unit tests for ammr.pddl (sexp, model, io, grounding, name scrambling)."""

from __future__ import annotations

import glob
from pathlib import Path

import pytest

from ammr.pddl.io import (
    UnsupportedPDDL,
    load_domain,
    load_problem,
    parse_domain,
    parse_problem,
    write_domain,
    write_problem,
)
from ammr.pddl.model import (
    ground_actions,
    ground_universe,
    scramble_names,
)
from ammr.pddl.sexp import parse, strip_comments, to_str


def test_sexp_parse_and_comments() -> None:
    raw = "; header comment\n(define (domain foo) ; inline\n  (:requirements :strips))\n"
    assert "comment" not in strip_comments(raw)
    expr = parse(raw)
    assert expr == ["define", ["domain", "foo"], [":requirements", ":strips"]]
    assert parse(to_str(expr)) == expr


def test_sexp_errors() -> None:
    with pytest.raises(ValueError):
        parse("   ; only comment")
    with pytest.raises(ValueError):
        parse("(a b")
    with pytest.raises(ValueError):
        parse(")a(")
    with pytest.raises(ValueError):
        parse("(a) (b)")


def test_unsupported_construct_rejected() -> None:
    bad = """
    (define (domain bad)
      (:requirements :strips)
      (:predicates (p ?x))
      (:action a :parameters (?x) :precondition (or (p ?x)) :effect (and)))
    """
    with pytest.raises(UnsupportedPDDL):
        parse_domain(bad)


@pytest.mark.parametrize("dom_path", sorted(glob.glob("domains/*/domain.pddl")))
def test_local_domains_exact_roundtrip(dom_path: str) -> None:
    dom = load_domain(dom_path)
    rt = parse_domain(write_domain(dom))
    assert rt == dom


@pytest.mark.parametrize(
    "dom_path",
    sorted(glob.glob("external/AMLGym/amlgym/benchmarks/domains/*.pddl")),
)
def test_amlgym_25_domains_exact_roundtrip(dom_path: str) -> None:
    dom = load_domain(dom_path)
    rt = parse_domain(write_domain(dom))
    assert rt == dom


def test_problem_roundtrip_and_transition_semantics() -> None:
    dom = load_domain("domains/blocksworld/domain.pddl")
    prob = load_problem("domains/blocksworld/problem_p01.pddl")
    assert parse_problem(write_problem(prob)) == prob

    # Checkground universe and initial applicability
    univ = ground_universe(dom, prob)
    assert prob.init <= univ
    app = [
        ga for ga in ground_actions(dom, prob) if dom.actions[ga[0]].is_applicable(prob.init, ga[1])
    ]
    assert len(app) > 0
    act_name, args = app[0]
    nxt = dom.actions[act_name].successor(prob.init, args)
    assert nxt <= univ
    assert nxt != prob.init


def test_equality_and_negative_preconditions() -> None:
    pddl_text = """
    (define (domain eqtest)
      (:requirements :strips :typing :equality :negative-preconditions)
      (:types box - object)
      (:predicates (marked ?b - box))
      (:action transfer
        :parameters (?a ?b - box)
        :precondition (and (marked ?a) (not (= ?a ?b)) (not (marked ?b)))
        :effect (and (not (marked ?a)) (marked ?b))))
    """
    dom = parse_domain(pddl_text)
    act = dom.actions["transfer"]
    s0 = frozenset({("marked", "b1")})
    assert not act.is_applicable(s0, ("b1", "b1"))
    assert act.is_applicable(s0, ("b1", "b2"))
    s1 = act.successor(s0, ("b1", "b2"))
    assert s1 == frozenset({("marked", "b2")})


def test_scramble_names_preserves_isomorphic_transitions() -> None:
    dom = load_domain("domains/barman/domain.pddl")
    prob = load_problem("domains/barman/problem_p01.pddl")
    s_dom, s_prob, mapping = scramble_names(dom, prob)

    # Original predicate and action names must not appear in scrambled domain
    assert set(s_dom.predicates).isdisjoint(set(dom.predicates))
    assert set(s_dom.actions).isdisjoint(set(dom.actions))

    # Applicable ground actions from s0 must have exact 1-to-1 bijection
    orig_app = [
        (mapping[name], args)
        for name, args in ground_actions(dom, prob)
        if dom.actions[name].is_applicable(prob.init, args)
    ]
    scram_app = [
        (name, args)
        for name, args in ground_actions(s_dom, s_prob)
        if s_dom.actions[name].is_applicable(s_prob.init, args)
    ]
    assert sorted(orig_app) == sorted(scram_app)
    assert parse_domain(write_domain(s_dom)) == s_dom
    assert Path("domains/barman/domain.pddl").exists()
