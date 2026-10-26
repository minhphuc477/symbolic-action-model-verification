"""Immutable STRIPS action-model representation.

Atoms are tuples ``(predicate, arg1, ..., argN)``. In action schemas the arguments are
variables (``?x``) or constants; in states they are object names. Equality atoms use the
predicate ``"="``.

Semantics follow PDDL: an action is applicable if all positive preconditions hold, no negative
precondition holds, and equality constraints are satisfied; the successor is
``(s - delete) | add``.
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field, replace
from itertools import product

Atom = tuple[str, ...]
State = frozenset[Atom]
Binding = Mapping[str, str]
GroundAction = tuple[str, tuple[str, ...]]

EQ = "="


def ground_atom(atom: Atom, binding: Binding) -> Atom:
    """Substitute variables in ``atom`` using ``binding`` (constants are left unchanged)."""
    return (atom[0], *(binding.get(t, t) for t in atom[1:]))


@dataclass(frozen=True)
class Action:
    """A lifted STRIPS action schema."""

    name: str
    params: tuple[tuple[str, str], ...]  # (variable, type)
    pre_pos: frozenset[Atom] = frozenset()
    pre_neg: frozenset[Atom] = frozenset()
    add: frozenset[Atom] = frozenset()
    delete: frozenset[Atom] = frozenset()

    @property
    def variables(self) -> tuple[str, ...]:
        return tuple(v for v, _ in self.params)

    def bind(self, args: Iterable[str]) -> dict[str, str]:
        args_t = tuple(args)
        if len(args_t) != len(self.params):
            raise ValueError(f"{self.name}: expected {len(self.params)} args, got {len(args_t)}")
        return dict(zip(self.variables, args_t))

    def is_applicable(self, state: State, args: Iterable[str]) -> bool:
        b = self.bind(args)
        for atom in self.pre_pos:
            if atom[0] == EQ:
                if b.get(atom[1], atom[1]) != b.get(atom[2], atom[2]):
                    return False
            elif ground_atom(atom, b) not in state:
                return False
        for atom in self.pre_neg:
            if atom[0] == EQ:
                if b.get(atom[1], atom[1]) == b.get(atom[2], atom[2]):
                    return False
            elif ground_atom(atom, b) in state:
                return False
        return True

    def successor(self, state: State, args: Iterable[str]) -> State:
        """Successor state; caller is responsible for checking applicability."""
        b = self.bind(args)
        dels = {ground_atom(a, b) for a in self.delete}
        adds = {ground_atom(a, b) for a in self.add}
        return frozenset((state - dels) | adds)

    def with_changes(self, **kwargs: frozenset[Atom]) -> Action:
        return replace(self, **kwargs)


@dataclass(frozen=True)
class Domain:
    name: str
    requirements: tuple[str, ...]
    types: Mapping[str, str]  # child -> parent ("object" is the root)
    constants: Mapping[str, str]  # constant -> type
    predicates: Mapping[str, tuple[str, ...]]  # name -> argument types
    actions: Mapping[str, Action]

    def with_action(self, action: Action) -> Domain:
        return replace(self, actions={**self.actions, action.name: action})

    def is_subtype(self, t: str, ancestor: str) -> bool:
        seen: set[str] = set()
        while t not in seen:
            if t == ancestor:
                return True
            seen.add(t)
            t = self.types.get(t, "object")
        return ancestor == "object"


@dataclass(frozen=True)
class Problem:
    name: str
    domain_name: str
    objects: Mapping[str, str]  # object -> type
    init: State
    goal_pos: frozenset[Atom]
    goal_neg: frozenset[Atom] = field(default_factory=frozenset)

    def goal_reached(self, state: State) -> bool:
        return self.goal_pos <= state and not (self.goal_neg & state)


def objects_of_type(domain: Domain, problem: Problem, typ: str) -> list[str]:
    pool = {**domain.constants, **problem.objects}
    return sorted(o for o, t in pool.items() if domain.is_subtype(t, typ))


def ground_actions(domain: Domain, problem: Problem) -> Iterator[GroundAction]:
    """Enumerate all type-correct groundings of every action (sorted, deterministic)."""
    for name in sorted(domain.actions):
        action = domain.actions[name]
        pools = [objects_of_type(domain, problem, t) for _, t in action.params]
        for args in product(*pools):
            yield name, tuple(args)


def ground_universe(domain: Domain, problem: Problem) -> frozenset[Atom]:
    """Return the complete universe of type-valid ground atoms for ``(domain, problem)``."""
    atoms: set[Atom] = set()
    for pred, arg_types in domain.predicates.items():
        pools = [objects_of_type(domain, problem, t) for t in arg_types]
        for args in product(*pools):
            atoms.add((pred, *args))
    return frozenset(atoms)


def format_ground(ga: GroundAction) -> str:
    name, args = ga
    return "(" + " ".join((name, *args)) + ")"


def scramble_names(
    domain: Domain, problem: Problem, seed: int = 0
) -> tuple[Domain, Problem, dict[str, str]]:
    """Deterministically replace custom types, predicates, and action names with shuffled IDs."""
    rng = random.Random(seed)
    mapping: dict[str, str] = {"object": "object", EQ: EQ}
    all_types = sorted((set(domain.types) | set(domain.types.values())) - {"object"})
    rng.shuffle(all_types)
    for idx, t in enumerate(all_types):
        mapping[t] = f"type_{idx:02d}"
    all_preds = sorted(domain.predicates)
    rng.shuffle(all_preds)
    for idx, p in enumerate(all_preds):
        mapping[p] = f"pred_{idx:02d}"
    all_acts = sorted(domain.actions)
    rng.shuffle(all_acts)
    for idx, a in enumerate(all_acts):
        mapping[a] = f"act_{idx:02d}"

    def _tr_atom(atom: Atom) -> Atom:
        return (mapping.get(atom[0], atom[0]), *atom[1:])

    def _tr_set(s: frozenset[Atom]) -> frozenset[Atom]:
        return frozenset(_tr_atom(a) for a in s)

    new_types = {mapping[c]: mapping[p] for c, p in domain.types.items() if c != "object"}
    new_consts = {c: mapping.get(t, t) for c, t in domain.constants.items()}
    new_preds = {
        mapping[p]: tuple(mapping.get(t, t) for t in ts) for p, ts in domain.predicates.items()
    }
    new_actions: dict[str, Action] = {}
    for name, act in domain.actions.items():
        new_name = mapping[name]
        new_params = tuple((v, mapping.get(t, t)) for v, t in act.params)
        new_actions[new_name] = Action(
            name=new_name,
            params=new_params,
            pre_pos=_tr_set(act.pre_pos),
            pre_neg=_tr_set(act.pre_neg),
            add=_tr_set(act.add),
            delete=_tr_set(act.delete),
        )
    s_dom = Domain(
        name=f"dom_{domain.name[:4]}_s",
        requirements=domain.requirements,
        types=new_types,
        constants=new_consts,
        predicates=new_preds,
        actions=new_actions,
    )
    s_prob = Problem(
        name=f"prob_{problem.name[:4]}_s",
        domain_name=s_dom.name,
        objects={o: mapping.get(t, t) for o, t in problem.objects.items()},
        init=_tr_set(problem.init),
        goal_pos=_tr_set(problem.goal_pos),
        goal_neg=_tr_set(problem.goal_neg),
    )
    return s_dom, s_prob, mapping
