"""Read and write PDDL domains/problems (STRIPS, typing, negative preconditions, equality).

Unsupported constructs (conditional effects, quantifiers, disjunctions, ``either`` types)
raise :class:`UnsupportedPDDL` so that a domain is excluded explicitly rather than silently
mis-parsed. Action-cost effects ``(increase (total-cost) n)`` are dropped: the repair task
concerns logical dynamics only, and plans are compared by length.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from ammr.pddl.model import EQ, Action, Atom, Domain, Problem
from ammr.pddl.sexp import SExp, parse, to_str


class UnsupportedPDDL(ValueError):
    """Raised for PDDL features outside the supported fragment."""


_UNSUPPORTED = {"forall", "exists", "when", "or", "imply", "either"}


def _typed_list(items: list[SExp]) -> list[tuple[str, str]]:
    """Parse ``a b - t c`` into ``[(a, t), (b, t), (c, object)]``."""
    out: list[tuple[str, str]] = []
    pending: list[str] = []
    i = 0
    while i < len(items):
        tok = items[i]
        if tok == "-":
            typ = items[i + 1]
            if not isinstance(typ, str):
                raise UnsupportedPDDL(f"complex type {to_str(typ)}")
            out.extend((p, typ) for p in pending)
            pending = []
            i += 2
            continue
        if not isinstance(tok, str):
            raise UnsupportedPDDL(f"unexpected list in typed list: {to_str(tok)}")
        pending.append(tok)
        i += 1
    out.extend((p, "object") for p in pending)
    return out


def _atom(expr: SExp) -> Atom:
    if isinstance(expr, str) or not expr or not all(isinstance(t, str) for t in expr):
        raise UnsupportedPDDL(f"not an atom: {to_str(expr)}")
    return tuple(expr)  # type: ignore[arg-type]


def _conjuncts(expr: SExp) -> list[SExp]:
    if expr == [] or expr == ["and"]:
        return []
    if isinstance(expr, list) and expr and expr[0] == "and":
        return [c for sub in expr[1:] for c in _conjuncts(sub)]
    if isinstance(expr, list) and expr and expr[0] in _UNSUPPORTED:
        raise UnsupportedPDDL(f"unsupported construct '{expr[0]}'")
    return [expr]


def _literals(expr: SExp) -> tuple[frozenset[Atom], frozenset[Atom]]:
    pos: set[Atom] = set()
    neg: set[Atom] = set()
    for lit in _conjuncts(expr):
        if isinstance(lit, list) and lit and lit[0] == "not":
            neg.add(_atom(lit[1]))
        else:
            pos.add(_atom(lit))
    return frozenset(pos), frozenset(neg)


def _effects(expr: SExp) -> tuple[frozenset[Atom], frozenset[Atom]]:
    add: set[Atom] = set()
    delete: set[Atom] = set()
    for lit in _conjuncts(expr):
        if isinstance(lit, list) and lit and lit[0] in ("increase", "decrease"):
            continue  # action costs: intentionally ignored (see module docstring)
        if isinstance(lit, list) and lit and lit[0] == "not":
            delete.add(_atom(lit[1]))
        else:
            add.add(_atom(lit))
    return frozenset(add), frozenset(delete)


def _sections(expr: list[SExp]) -> dict[str, list[SExp]]:
    out: dict[str, list[SExp]] = {}
    for item in expr[2:]:
        if isinstance(item, list) and item and isinstance(item[0], str):
            out.setdefault(item[0], []).append(item)
    return out


def _parse_action(expr: list[SExp]) -> Action:
    name = expr[1]
    fields: dict[str, SExp] = {}
    for i in range(2, len(expr) - 1, 2):
        fields[str(expr[i])] = expr[i + 1]
    params = _typed_list(fields.get(":parameters", []))  # type: ignore[arg-type]
    pre_pos, pre_neg = _literals(fields.get(":precondition", []))
    add, delete = _effects(fields.get(":effect", []))
    return Action(str(name), tuple(params), pre_pos, pre_neg, add, delete)


def _canonical_requirements(
    raw_reqs: set[str],
    types: Mapping[str, str],
    constants: Mapping[str, str],
    predicates: Mapping[str, tuple[str, ...]],
    actions: Mapping[str, Action],
) -> tuple[str, ...]:
    reqs = (set(raw_reqs) - {":action-costs"}) | {":strips"}
    uses_typing = (
        bool(types)
        or any(t != "object" for t in constants.values())
        or any(t != "object" for ts in predicates.values() for t in ts)
        or any(t != "object" for a in actions.values() for _, t in a.params)
    )
    if uses_typing:
        reqs.add(":typing")
    if any(a.pre_neg for a in actions.values()):
        reqs.add(":negative-preconditions")
    if any(atom[0] == EQ for a in actions.values() for atom in (*a.pre_pos, *a.pre_neg)):
        reqs.add(":equality")
    return tuple(sorted(reqs))


def parse_domain(text: str) -> Domain:
    expr = parse(text)
    if not (isinstance(expr, list) and expr[0] == "define"):
        raise ValueError("not a PDDL define block")
    name = str(expr[1][1])  # type: ignore[index]
    sec = _sections(expr)
    raw_reqs = {str(r) for r in sec.get(":requirements", [[None]])[0][1:] if r is not None}
    raw_types = {c: p for c, p in _typed_list(sec.get(":types", [[None]])[0][1:]) if c != "object"}
    # Ensure every referenced non-object parent type is registered under "object"
    for parent in list(raw_types.values()):
        if parent != "object" and parent not in raw_types:
            raw_types[parent] = "object"
    constants = dict(_typed_list(sec.get(":constants", [[None]])[0][1:]))
    predicates: dict[str, tuple[str, ...]] = {}
    for pred in sec.get(":predicates", [[None]])[0][1:]:
        if not isinstance(pred, list):
            raise UnsupportedPDDL(f"bad predicate {pred}")
        predicates[str(pred[0])] = tuple(t for _, t in _typed_list(pred[1:]))
    actions: dict[str, Action] = {}
    for act in sec.get(":action", []):
        a = _parse_action(act)
        actions[a.name] = a
    if sec.get(":durative-action") or sec.get(":derived"):
        raise UnsupportedPDDL("durative actions / derived predicates")
    reqs = _canonical_requirements(raw_reqs, raw_types, constants, predicates, actions)
    return Domain(name, reqs, raw_types, constants, predicates, actions)


def parse_problem(text: str) -> Problem:
    expr = parse(text)
    name = str(expr[1][1])  # type: ignore[index]
    sec = _sections(expr)
    domain_name = str(sec[":domain"][0][1])
    objects = dict(_typed_list(sec.get(":objects", [[None]])[0][1:]))
    init: set[Atom] = set()
    for fact in sec[":init"][0][1:]:
        if isinstance(fact, list) and fact and fact[0] == EQ:
            continue  # numeric fluent initialisation, e.g. (= (total-cost) 0)
        init.add(_atom(fact))
    goal_pos, goal_neg = _literals(sec[":goal"][0][1])
    return Problem(name, domain_name, objects, frozenset(init), goal_pos, goal_neg)


def load_domain(path: str | Path) -> Domain:
    return parse_domain(Path(path).read_text(encoding="utf-8"))


def load_problem(path: str | Path) -> Problem:
    return parse_problem(Path(path).read_text(encoding="utf-8"))


def _fmt_atom(atom: Atom) -> str:
    return "(" + " ".join(atom) + ")"


def _fmt_conj(pos: frozenset[Atom], neg: frozenset[Atom] = frozenset()) -> str:
    lits = [_fmt_atom(a) for a in sorted(pos)] + [f"(not {_fmt_atom(a)})" for a in sorted(neg)]
    return "(and " + " ".join(lits) + ")" if lits else "(and)"


def _fmt_typed(pairs: list[tuple[str, str]], typed: bool) -> str:
    """Format a typed list. When ``typed`` is True, explicit ``- type`` prevents grouping bugs."""
    if not typed:
        return " ".join(n for n, _ in pairs)
    return " ".join(f"{n} - {t}" for n, t in pairs)


def _topo_types(types: Mapping[str, str]) -> list[tuple[str, str]]:
    """Order types so parent types precede children."""
    ordered: list[tuple[str, str]] = []
    emitted: set[str] = {"object"}
    remaining = dict(types)
    while remaining:
        progressed = False
        for child in sorted(list(remaining)):
            parent = remaining[child]
            if parent in emitted:
                ordered.append((child, parent))
                emitted.add(child)
                del remaining[child]
                progressed = True
        if not progressed:
            ordered.extend(sorted(remaining.items()))
            break
    return ordered


def write_domain(d: Domain) -> str:
    reqs = _canonical_requirements(
        set(d.requirements), d.types, d.constants, d.predicates, d.actions
    )
    typed = ":typing" in reqs
    lines = [f"(define (domain {d.name})", f"  (:requirements {' '.join(reqs)})"]
    if d.types:
        lines.append(f"  (:types {_fmt_typed(_topo_types(d.types), typed=True)})")
    if d.constants:
        lines.append(f"  (:constants {_fmt_typed(sorted(d.constants.items()), typed=typed)})")
    preds = []
    for p, ts in sorted(d.predicates.items()):
        args = _fmt_typed([(f"?a{i}", t) for i, t in enumerate(ts)], typed=typed)
        preds.append(f"({p} {args})" if args else f"({p})")
    lines.append(f"  (:predicates {' '.join(preds)})")
    for name in sorted(d.actions):
        a = d.actions[name]
        lines += [
            f"  (:action {a.name}",
            f"    :parameters ({_fmt_typed(list(a.params), typed=typed)})",
            f"    :precondition {_fmt_conj(a.pre_pos, a.pre_neg)}",
            f"    :effect {_fmt_conj(a.add, a.delete)})",
        ]
    lines.append(")")
    return "\n".join(lines) + "\n"


def write_problem(p: Problem) -> str:
    typed = any(t != "object" for t in p.objects.values())
    objs = _fmt_typed(sorted(p.objects.items()), typed=typed)
    init = " ".join(_fmt_atom(a) for a in sorted(p.init))
    return (
        f"(define (problem {p.name}) (:domain {p.domain_name})\n"
        f"  (:objects {objs})\n  (:init {init})\n"
        f"  (:goal {_fmt_conj(p.goal_pos, p.goal_neg)}))\n"
    )
