"""Isolated execution environment with explicit observation modes.

``Environment`` encapsulates the ground-truth domain privately using Python name
mangling so that no learner or baseline can inspect ``M*``. All interaction happens
exclusively through :meth:`reset` and :meth:`step`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import StrEnum

from ammr.pddl.model import Atom, Domain, GroundAction, Problem, State, ground_universe


class ObservationMode(StrEnum):
    BINARY = "binary"
    PARTIAL = "partial"
    FULL = "full"


class BudgetExhausted(RuntimeError):
    """Raised when an agent attempts more environment steps than ``step_budget``."""


@dataclass(frozen=True)
class PartialState:
    """Observed truth values of ground atoms: ``pos`` = known true, ``neg`` = known false."""

    pos: frozenset[Atom] = frozenset()
    neg: frozenset[Atom] = frozenset()


@dataclass(frozen=True)
class StepOutcome:
    """Single-step environment feedback returned by :meth:`Environment.step`."""

    action: GroundAction
    applicable: bool
    obs_before: PartialState
    obs_after: PartialState
    goal_reached: bool


class Environment:
    """Stateful execution oracle with configurable observability and step budget."""

    def __init__(
        self,
        true_domain: Domain,
        problem: Problem,
        mode: ObservationMode = ObservationMode.FULL,
        obs_prob: float = 1.0,
        step_budget: int = 200,
        seed: int = 0,
    ) -> None:
        if mode == ObservationMode.PARTIAL and not (0.0 < obs_prob < 1.0):
            raise ValueError(f"partial mode requires 0 < obs_prob < 1, got {obs_prob}")
        self.__true_domain = true_domain
        self._problem = problem
        self._universe = tuple(sorted(ground_universe(true_domain, problem)))
        self._universe_set = frozenset(self._universe)
        self.mode = mode
        self.obs_prob = (
            1.0
            if mode == ObservationMode.FULL
            else (0.0 if mode == ObservationMode.BINARY else obs_prob)
        )
        self.step_budget = step_budget
        self._rng = random.Random(seed)
        self._state: State = problem.init
        self._steps_used = 0

    @property
    def steps_used(self) -> int:
        return self._steps_used

    @property
    def remaining_steps(self) -> int:
        return max(0, self.step_budget - self._steps_used)

    def goal_reached(self) -> bool:
        return self._problem.goal_reached(self._state)

    def _observe(self, state: State) -> PartialState:
        if self.mode == ObservationMode.BINARY:
            return PartialState()
        if self.mode == ObservationMode.FULL:
            return PartialState(pos=state, neg=self._universe_set - state)
        mask = frozenset(g for g in self._universe if self._rng.random() < self.obs_prob)
        return PartialState(pos=state & mask, neg=mask - state)

    def reset(self) -> PartialState:
        """Reset current state to ``problem.init`` without consuming step budget."""
        self._state = self._problem.init
        return self._observe(self._state)

    def step(self, action: GroundAction) -> StepOutcome:
        """Attempt ``action`` in the current state; consumes 1 step from ``step_budget``."""
        if self._steps_used >= self.step_budget:
            raise BudgetExhausted(f"step budget ({self.step_budget}) exhausted")
        self._steps_used += 1
        obs_before = self._observe(self._state)
        act_name, args = action
        schema = self.__true_domain.actions.get(act_name)
        if schema is not None and schema.is_applicable(self._state, args):
            self._state = schema.successor(self._state, args)
            applicable = True
        else:
            applicable = False
        obs_after = self._observe(self._state)
        return StepOutcome(
            action=action,
            applicable=applicable,
            obs_before=obs_before,
            obs_after=obs_after,
            goal_reached=self._problem.goal_reached(self._state),
        )
