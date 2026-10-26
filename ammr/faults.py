"""Seeded random fault injection across the 4 structural fault families.

Follows the random-injection evaluation methodology of Lin et al. (AAAI 2025): edits are
sampled uniformly from all syntactically type-valid schema edits using an explicit seed,
never hand-selected.
"""

from __future__ import annotations

import itertools
import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from ammr.pddl.io import write_domain
from ammr.pddl.model import Action, Atom, Domain, Problem, ground_actions


class FaultFamily(StrEnum):
    MISSING_PREC = "missing_prec"
    SPURIOUS_PREC = "spurious_prec"
    CORRUPT_EFFECT = "corrupt_effect"
    COMPOUND = "compound"


@dataclass(frozen=True, order=True)
class AtomicEdit:
    action: str
    kind: str  # rem_pre_pos | rem_pre_neg | add_pre_pos | rem_add | rem_del | add_add | add_del
    atom: Atom


@dataclass(frozen=True)
class FaultSpec:
    family: FaultFamily
    edits: tuple[AtomicEdit, ...]
    seed: int


def lifted_atom_candidates(domain: Domain, action: Action) -> tuple[Atom, ...]:
    """Return sorted type-compatible lifted atoms over ``action.params`` and domain constants."""
    cands: set[Atom] = set()
    for pred, arg_types in domain.predicates.items():
        pools: list[list[str]] = []
        for pt in arg_types:
            var_matches = [v for v, vt in action.params if domain.is_subtype(vt, pt)]
            const_matches = [c for c, ct in domain.constants.items() if domain.is_subtype(ct, pt)]
            pools.append(var_matches + const_matches)
        for tup in itertools.product(*pools):
            vars_only = [x for x in tup if x.startswith("?")]
            if len(set(vars_only)) == len(vars_only):
                cands.add((pred, *tup))
    return tuple(sorted(cands))


def dynamic_predicates(domain: Domain) -> frozenset[str]:
    """Predicates that appear in at least one action's add or delete list in ``domain``."""
    return frozenset(atom[0] for act in domain.actions.values() for atom in (*act.add, *act.delete))


def apply_edit(domain: Domain, edit: AtomicEdit) -> Domain:
    act = domain.actions[edit.action]
    atom = edit.atom
    match edit.kind:
        case "rem_pre_pos":
            updated = act.with_changes(pre_pos=act.pre_pos - {atom})
        case "rem_pre_neg":
            updated = act.with_changes(pre_neg=act.pre_neg - {atom})
        case "add_pre_pos":
            updated = act.with_changes(pre_pos=act.pre_pos | {atom})
        case "rem_add":
            updated = act.with_changes(add=act.add - {atom})
        case "rem_del":
            updated = act.with_changes(delete=act.delete - {atom})
        case "add_add":
            updated = act.with_changes(add=(act.add | {atom}), delete=act.delete - {atom})
        case "add_del":
            updated = act.with_changes(delete=(act.delete | {atom}), add=act.add - {atom})
        case _:
            raise ValueError(f"unknown edit kind: {edit.kind}")
    return domain.with_action(updated)


def apply_fault(domain: Domain, fault: FaultSpec) -> Domain:
    cur = domain
    for edit in fault.edits:
        cur = apply_edit(cur, edit)
    return cur


def enumerate_single_edits(domain: Domain, family: FaultFamily) -> list[AtomicEdit]:
    """Deterministically list all valid atomic edits belonging to ``family``."""
    dyn = dynamic_predicates(domain)
    out: list[AtomicEdit] = []
    for name in sorted(domain.actions):
        act = domain.actions[name]
        cands = lifted_atom_candidates(domain, act)
        if family in (FaultFamily.MISSING_PREC, FaultFamily.COMPOUND):
            for atom in sorted(act.pre_pos):
                if atom[0] != "=":
                    out.append(AtomicEdit(name, "rem_pre_pos", atom))
            for atom in sorted(act.pre_neg):
                if atom[0] != "=":
                    out.append(AtomicEdit(name, "rem_pre_neg", atom))
        if family in (FaultFamily.SPURIOUS_PREC, FaultFamily.COMPOUND):
            for atom in cands:
                if atom not in act.pre_pos and atom not in act.pre_neg:
                    out.append(AtomicEdit(name, "add_pre_pos", atom))
        if family in (FaultFamily.CORRUPT_EFFECT, FaultFamily.COMPOUND):
            for atom in sorted(act.add):
                out.append(AtomicEdit(name, "rem_add", atom))
            for atom in sorted(act.delete):
                out.append(AtomicEdit(name, "rem_del", atom))
            for atom in cands:
                if atom[0] in dyn and atom not in act.add and atom not in act.delete:
                    out.append(AtomicEdit(name, "add_add", atom))
                    out.append(AtomicEdit(name, "add_del", atom))
    return out


def _has_behavioral_difference(
    true_dom: Domain, cand_dom: Domain, problems: Sequence[Problem]
) -> bool:
    """Check whether ``cand_dom`` differs from ``true_dom`` on ``init`` ground transitions."""
    if not problems:
        return true_dom != cand_dom
    for prob in problems:
        for name, args in ground_actions(true_dom, prob):
            a_t, a_c = true_dom.actions[name], cand_dom.actions[name]
            app_t = a_t.is_applicable(prob.init, args)
            app_c = a_c.is_applicable(prob.init, args)
            if app_t != app_c:
                return True
            if app_t and a_t.successor(prob.init, args) != a_c.successor(prob.init, args):
                return True
    return true_dom != cand_dom


def sample_faults(
    domain: Domain,
    family: FaultFamily,
    count: int,
    k_edits: int = 1,
    seed: int = 0,
    problems: Sequence[Problem] = (),
) -> list[tuple[Domain, FaultSpec, bool]]:
    """Uniformly sample ``count`` distinct faults with ``k_edits`` edits using ``seed``."""
    rng = random.Random(seed)
    pool = enumerate_single_edits(domain, family)
    if len(pool) < k_edits:
        raise ValueError(f"domain {domain.name}: pool size {len(pool)} < k_edits={k_edits}")
    results: list[tuple[Domain, FaultSpec, bool]] = []
    seen_sigs: set[str] = {write_domain(domain)}
    attempts = 0
    max_attempts = max(200, count * 40)
    while len(results) < count and attempts < max_attempts:
        attempts += 1
        chosen = tuple(sorted(rng.sample(pool, k_edits)))
        # Avoid contradicting edits on the same (action, atom)
        targets = [(e.action, e.atom) for e in chosen]
        if len(set(targets)) < len(targets):
            continue
        spec = FaultSpec(family=family, edits=chosen, seed=seed + attempts)
        mutated = apply_fault(domain, spec)
        sig = write_domain(mutated)
        if sig in seen_sigs:
            continue
        seen_sigs.add(sig)
        impact = _has_behavioral_difference(domain, mutated, problems)
        results.append((mutated, spec, impact))
    return results
