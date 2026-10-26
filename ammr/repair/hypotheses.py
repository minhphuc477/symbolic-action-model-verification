"""Lifted version-space constraints over STRIPS action schemas.

Maintains exact forced/forbidden effect sets, forbidden precondition sets, and disjunctive
conflict clauses induced by positive and negative environment steps under full, partial, or
binary observability.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from ammr.env import PartialState, StepOutcome
from ammr.faults import lifted_atom_candidates
from ammr.pddl.model import Action, Atom, Domain, ground_atom

PreLit = tuple[bool, Atom]  # (True, atom) -> pre_pos; (False, atom) -> pre_neg


@dataclass(frozen=True)
class ConflictClause:
    """Disjunction of candidate precondition literals, at least one of which must hold."""

    literals: frozenset[PreLit]
    provisional: bool = False


@dataclass
class ActionHypothesis:
    """Version-space constraints accumulated for a single lifted action schema."""

    action_name: str
    candidates: tuple[Atom, ...]
    allow_neg_pre: bool = False
    forbidden_pre_pos: set[Atom] = field(default_factory=set)
    forbidden_pre_neg: set[Atom] = field(default_factory=set)
    prov_forbidden_pre_pos: set[Atom] = field(default_factory=set)
    prov_forbidden_pre_neg: set[Atom] = field(default_factory=set)
    forced_add: set[Atom] = field(default_factory=set)
    forbidden_add: set[Atom] = field(default_factory=set)
    forced_del: set[Atom] = field(default_factory=set)
    forbidden_del: set[Atom] = field(default_factory=set)
    conflicts: list[ConflictClause] = field(default_factory=list)

    def record_positive(
        self,
        schema: Action,
        args: tuple[str, ...],
        obs_before: PartialState,
        obs_after: PartialState,
        provisional: bool = False,
    ) -> None:
        b = schema.bind(args)
        grounded = {c: ground_atom(c, b) for c in self.candidates}
        counts = Counter(grounded.values())
        f_pos = self.prov_forbidden_pre_pos if provisional else self.forbidden_pre_pos
        f_neg = self.prov_forbidden_pre_neg if provisional else self.forbidden_pre_neg

        for c, g in grounded.items():
            if g in obs_before.neg:
                f_pos.add(c)
            if g in obs_before.pos:
                f_neg.add(c)
            if provisional:
                continue
            unique = counts[g] == 1
            if g in obs_after.neg:
                self.forbidden_add.add(c)
                if unique and g in obs_before.pos:
                    self.forced_del.add(c)
                    self.forbidden_add.add(c)
            if unique and g in obs_after.pos:
                self.forbidden_del.add(c)
                if g in obs_before.neg:
                    self.forced_add.add(c)
                    self.forbidden_del.add(c)

    def record_negative(
        self,
        schema: Action,
        args: tuple[str, ...],
        obs_before: PartialState,
        provisional: bool = False,
    ) -> None:
        b = schema.bind(args)
        grounded = {c: ground_atom(c, b) for c in self.candidates}
        lits: set[PreLit] = {(True, c) for c, g in grounded.items() if g not in obs_before.pos}
        if self.allow_neg_pre:
            lits |= {(False, c) for c, g in grounded.items() if g not in obs_before.neg}
        if not lits:
            return
        clause = ConflictClause(frozenset(lits), provisional=provisional)
        # Subsumption cleanup among clauses of equal or weaker certainty
        kept: list[ConflictClause] = []
        for existing in self.conflicts:
            if not existing.provisional and clause.provisional:
                if existing.literals <= clause.literals:
                    return
                kept.append(existing)
            elif existing.provisional == clause.provisional:
                if existing.literals <= clause.literals:
                    return
                if not (clause.literals < existing.literals):
                    kept.append(existing)
            else:
                # New verified clause subsumes an older provisional superclause
                if not (clause.literals <= existing.literals):
                    kept.append(existing)
        kept.append(clause)
        self.conflicts = kept

    def is_action_consistent(self, act: Action) -> bool:
        """Check consistency against verified (non-provisional) constraints only."""
        if act.pre_pos & self.forbidden_pre_pos:
            return False
        if act.pre_neg & self.forbidden_pre_neg:
            return False
        if not (self.forced_add <= act.add) or (act.add & self.forbidden_add):
            return False
        if not (self.forced_del <= act.delete) or (act.delete & self.forbidden_del):
            return False
        act_lits: set[PreLit] = {(True, a) for a in act.pre_pos} | {(False, a) for a in act.pre_neg}
        return all(c.provisional or bool(c.literals & act_lits) for c in self.conflicts)


class DomainVersionSpace:
    """Domain-wide version space across all action schemas."""

    def __init__(self, prior_domain: Domain, allow_neg_pre: bool | None = None) -> None:
        use_neg = (
            (":negative-preconditions" in prior_domain.requirements)
            if allow_neg_pre is None
            else allow_neg_pre
        )
        self.allow_neg_pre = use_neg
        self.actions: dict[str, ActionHypothesis] = {
            name: ActionHypothesis(
                action_name=name,
                candidates=lifted_atom_candidates(prior_domain, act),
                allow_neg_pre=use_neg,
            )
            for name, act in prior_domain.actions.items()
        }
        self._schemas: dict[str, Action] = dict(prior_domain.actions)
        self.refuted_domains: set[str] = set()

    def observe_step(
        self,
        outcome: StepOutcome,
        fallback_before: PartialState | None = None,
        provisional: bool = False,
    ) -> None:
        act_name, args = outcome.action
        hyp = self.actions[act_name]
        schema = self._schemas[act_name]
        obs0 = fallback_before if fallback_before is not None else outcome.obs_before
        if outcome.applicable:
            hyp.record_positive(schema, args, obs0, outcome.obs_after, provisional=provisional)
        else:
            hyp.record_negative(schema, args, obs0, provisional=provisional)

    def is_domain_consistent(self, domain: Domain) -> bool:
        return all(
            self.actions[name].is_action_consistent(act) for name, act in domain.actions.items()
        )
