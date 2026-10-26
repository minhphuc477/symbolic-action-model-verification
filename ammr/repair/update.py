"""Minimum-cardinality edit projection onto the lifted version space."""

from __future__ import annotations

from typing import Literal

from ammr.faults import dynamic_predicates
from ammr.pddl.model import Action, Atom, Domain
from ammr.repair.hypotheses import ActionHypothesis, DomainVersionSpace, PreLit

TieBreak = Literal["lex", "coherence"]


def _simplify_clauses(clauses: list[frozenset[PreLit]]) -> list[frozenset[PreLit]]:
    unique = sorted({c for c in clauses if c}, key=lambda c: (len(c), sorted(c)))
    minimal: list[frozenset[PreLit]] = []
    for c in unique:
        if not any(m <= c for m in minimal):
            minimal.append(c)
    return minimal


def solve_min_hitting_sets(
    clauses: list[frozenset[PreLit]], max_solutions: int = 8
) -> list[frozenset[PreLit]]:
    """Return exact minimum-cardinality non-contradictory hitting sets (up to ``max_solutions``)."""
    simplified = _simplify_clauses(clauses)
    if not simplified:
        return [frozenset()]

    # Fast path for size-1 hitting sets (set intersection)
    common = set(simplified[0]).intersection(*simplified[1:])
    if common:
        ordered = sorted(common)
        return [frozenset({lit}) for lit in ordered[:max_solutions]]

    solutions: list[frozenset[PreLit]] = []
    seen: set[frozenset[PreLit]] = set()

    def _dfs(rem: list[frozenset[PreLit]], chosen: frozenset[PreLit], budget: int) -> None:
        if len(solutions) >= max_solutions:
            return
        if not rem:
            if chosen not in seen:
                seen.add(chosen)
                solutions.append(chosen)
            return
        if budget == 0:
            return
        c0 = min(rem, key=len)
        used_atoms = {a for _, a in chosen}
        for lit in sorted(c0):
            if lit[1] in used_atoms:
                continue
            nxt_rem = [c for c in rem if lit not in c]
            _dfs(nxt_rem, chosen | {lit}, budget - 1)
            if len(solutions) >= max_solutions:
                return

    for limit in range(2, len(simplified) + 1):
        _dfs(simplified, frozenset(), limit)
        if solutions:
            return solutions
    return [frozenset()]


def _rank_hitting_set(
    hset: frozenset[PreLit],
    new_add: frozenset[Atom],
    new_del: frozenset[Atom],
    dyn_preds: frozenset[str],
    tie_break: TieBreak,
) -> tuple[object, ...]:
    ordered = tuple(sorted(hset))
    if tie_break == "lex":
        return (ordered,)
    tier_sum = 0
    for sign, atom in ordered:
        if sign:
            if atom in new_del and atom not in new_add:
                tier = 0
            elif atom not in new_add and atom[0] in dyn_preds:
                tier = 1
            elif atom not in new_add:
                tier = 2
            else:
                tier = 3
        else:
            tier = 1 if atom[0] in dyn_preds else 2
        tier_sum += tier
    return (tier_sum, ordered)


def project_action_candidates(
    prior_act: Action,
    hyp: ActionHypothesis,
    dyn_preds: frozenset[str],
    tie_break: TieBreak = "lex",
    max_variants: int = 6,
) -> list[Action]:
    """Return minimum-edit projections of ``prior_act`` ordered by ``tie_break``."""
    new_add = frozenset((prior_act.add - hyp.forbidden_add) | hyp.forced_add)
    new_del = frozenset(((prior_act.delete - hyp.forbidden_del) | hyp.forced_del) - new_add)

    # Verified forbidden sets take strict precedence; provisional ones apply if consistent
    forb_pos = set(hyp.forbidden_pre_pos)
    forb_neg = set(hyp.forbidden_pre_neg)
    all_forb: set[PreLit] = {(True, a) for a in forb_pos | hyp.prov_forbidden_pre_pos} | {
        (False, a) for a in forb_neg | hyp.prov_forbidden_pre_neg
    }
    ver_forb: set[PreLit] = {(True, a) for a in forb_pos} | {(False, a) for a in forb_neg}

    prior_lits: set[PreLit] = {(True, a) for a in prior_act.pre_pos} | {
        (False, a) for a in prior_act.pre_neg
    }
    kept_prior = prior_lits - all_forb
    kept_atoms = {a for _, a in kept_prior}

    active_clauses: list[frozenset[PreLit]] = []
    for c in hyp.conflicts:
        if c.literals & kept_prior:
            continue
        filtered = frozenset(lit for lit in (c.literals - all_forb) if lit[1] not in kept_atoms)
        if filtered:
            active_clauses.append(filtered)
        elif not c.provisional:
            fallback = frozenset(lit for lit in (c.literals - ver_forb) if lit[1] not in kept_atoms)
            if fallback:
                active_clauses.append(fallback)

    hsets = solve_min_hitting_sets(active_clauses, max_solutions=max_variants)
    hsets.sort(key=lambda h: _rank_hitting_set(h, new_add, new_del, dyn_preds, tie_break))

    variants: list[Action] = []
    for h in hsets:
        merged = kept_prior | h
        pre_pos = frozenset(a for s, a in merged if s)
        pre_neg = frozenset(a for s, a in merged if not s)
        variants.append(
            Action(prior_act.name, prior_act.params, pre_pos, pre_neg, new_add, new_del)
        )
    return variants


def project_action(
    prior_act: Action,
    hyp: ActionHypothesis,
    dyn_preds: frozenset[str],
    tie_break: TieBreak = "lex",
) -> Action:
    return project_action_candidates(prior_act, hyp, dyn_preds, tie_break, max_variants=8)[0]


def project_domain(
    prior_domain: Domain, vspace: DomainVersionSpace, tie_break: TieBreak = "lex"
) -> Domain:
    dyn = dynamic_predicates(prior_domain)
    actions = {
        name: project_action(act, vspace.actions[name], dyn, tie_break=tie_break)
        for name, act in prior_domain.actions.items()
    }
    return Domain(
        name=prior_domain.name,
        requirements=prior_domain.requirements,
        types=prior_domain.types,
        constants=prior_domain.constants,
        predicates=prior_domain.predicates,
        actions=actions,
    )
