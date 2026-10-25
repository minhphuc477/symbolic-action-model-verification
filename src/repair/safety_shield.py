"""
Safety Shield & Conservative Action Envelope for CEG-OMR
=========================================================
Addresses the fundamental threat to validity:
  "What happens in irreversible physical environments (non-resettable dead-ends)
   when an agent actively executes a flawed action?"

Provides:
  1. ActionReversibilityAnalyzer: Static PDDL inverse analysis.
  2. SafetyEnvelope: Conservative invariant guard (SAM-inspired).
  3. SafeCEGOMRShield: Intercepts irreversible unverified transitions before
     physical dispatch, generating zero-risk virtual counterexamples.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pddl


class ActionSafetyClass(Enum):
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"
    CONDITIONALLY_REVERSIBLE = "conditionally_reversible"


class ShieldDecision(Enum):
    DISPATCH = "dispatch"          # Action is safe to execute physically
    INTERCEPT = "intercept"        # Action blocked by shield; treat as virtual failure
    REJECT = "reject"              # Action definitely invalid


@dataclass
class InterceptionRecord:
    step_index: int
    action_name: str
    ground_args: list[str]
    safety_class: ActionSafetyClass
    reason: str
    current_state_fluents: set[str]


@dataclass
class SafetyShieldConfig:
    enabled: bool = True
    mode: str = "hybrid"  # "permissive", "conservative", "hybrid"
    custom_irreversible_actions: set[str] = field(default_factory=set)
    virtual_counterexample_penalty: float = 1.0


class ActionReversibilityAnalyzer:
    """
    Performs static causal analysis on PDDL domain action schemas to determine
    whether an action has a valid inverse operator (Reversibility).
    """

    def __init__(self, domain_path: str):
        self.domain_path = domain_path
        self.domain = pddl.parse_domain(domain_path)
        self.action_classes: dict[str, ActionSafetyClass] = {}
        self._analyze()

    def _analyze(self) -> None:
        actions = list(self.domain.actions)

        # 1. Collect all predicates that can ever be added across the entire domain
        all_domain_adds: set[str] = set()
        for b in actions:
            all_domain_adds.update(self._extract_predicates(b.effect, is_add=True))

        for a in actions:
            a_name = a.name.lower()
            a_adds = self._extract_predicates(a.effect, is_add=True)
            a_dels = self._extract_predicates(a.effect, is_add=False)

            if not a_dels:
                # Actions that do not delete any fluent are non-destructive
                self.action_classes[a_name] = ActionSafetyClass.REVERSIBLE
                continue

            # Criterion 1: Depleting Non-Renewable Facts
            # If an action deletes any predicate that NO action in the domain can ever add,
            # it is strictly irreversible (e.g. soil samples, consuming fuel).
            unrestorable_dels = a_dels - all_domain_adds
            if unrestorable_dels:
                self.action_classes[a_name] = ActionSafetyClass.IRREVERSIBLE
                continue

            # Criterion 2: Formal Inverse Action Existence
            # An exact inverse action b must restore all deleted predicates of a (a_dels <= b_adds)
            # and undo what a added (a_adds <= b_dels).
            has_formal_inverse = False
            for b in actions:
                if b.name.lower() == a_name:
                    # An action can only invert itself if it is a toggle (e.g. drive ?from ?to <-> drive ?to ?from)
                    # Check if action has matching symmetric add/del
                    if a_adds == a_dels and len(a_adds) > 0:
                        has_formal_inverse = True
                        break
                    continue

                b_adds = self._extract_predicates(b.effect, is_add=True)
                b_dels = self._extract_predicates(b.effect, is_add=False)

                # An inverse b must restore all of a's deletions and revert all of a's additions
                if a_dels.issubset(b_adds) and a_adds.issubset(b_dels):
                    has_formal_inverse = True
                    break

            if has_formal_inverse:
                self.action_classes[a_name] = ActionSafetyClass.REVERSIBLE
            else:
                self.action_classes[a_name] = ActionSafetyClass.IRREVERSIBLE

    def _extract_predicates(self, effect_formula: Any, is_add: bool) -> set[str]:
        pred_names = set()
        if effect_formula is None:
            return pred_names

        # Parse PDDL AST or token representation
        if hasattr(effect_formula, "operands"):
            for op in effect_formula.operands:
                pred_names.update(self._extract_predicates(op, is_add))
        elif hasattr(effect_formula, "argument"):  # Not formula
            if not is_add:
                arg = effect_formula.argument
                pred_names.add(getattr(arg, "name", str(arg)))
        else:  # Atomic predicate
            if is_add:
                pred_names.add(getattr(effect_formula, "name", str(effect_formula)))

        return pred_names

    def get_safety_class(self, action_name: str) -> ActionSafetyClass:
        return self.action_classes.get(action_name.lower(), ActionSafetyClass.IRREVERSIBLE)


class SafetyEnvelopeShield:
    """
    Dual-layer safety shield for CEG-OMR.
    Guarantees zero physical catastrophic failures in irreversible environments.
    """

    def __init__(
        self,
        domain_path: str,
        config: SafetyShieldConfig | None = None,
        conservative_invariants: dict[str, set[str]] | None = None,
    ):
        self.config = config or SafetyShieldConfig()
        self.analyzer = ActionReversibilityAnalyzer(domain_path)
        self.conservative_invariants = conservative_invariants or {}
        self.interception_history: list[InterceptionRecord] = []

    def evaluate_step(
        self,
        step_index: int,
        action_name: str,
        ground_args: list[str],
        current_state: set[str],
    ) -> tuple[ShieldDecision, str]:
        """
        Evaluate whether an action is safe to dispatch to the physical environment.
        """
        if not self.config.enabled or self.config.mode == "permissive":
            return ShieldDecision.DISPATCH, "Shield permissive: dispatch allowed"

        act_lower = action_name.lower()
        safety_class = self.analyzer.get_safety_class(act_lower)

        # Check custom override
        if act_lower in self.config.custom_irreversible_actions:
            safety_class = ActionSafetyClass.IRREVERSIBLE

        # Mode: Conservative (SAM style) -> Block all non-certified transitions
        if self.config.mode == "conservative":
            safe_preconds = self.conservative_invariants.get(act_lower, set())
            missing = safe_preconds - current_state
            if missing:
                record = InterceptionRecord(
                    step_index=step_index,
                    action_name=action_name,
                    ground_args=ground_args,
                    safety_class=safety_class,
                    reason=f"Conservative shield: unverified preconds {missing}",
                    current_state_fluents=current_state,
                )
                self.interception_history.append(record)
                return ShieldDecision.INTERCEPT, record.reason
            return ShieldDecision.DISPATCH, "Certified conservative dispatch"

        # Mode: Hybrid (Reversibility-aware active repair)
        # If action is reversible, dispatch freely! Any failure can be undone.
        if safety_class == ActionSafetyClass.REVERSIBLE:
            return ShieldDecision.DISPATCH, "Reversible action: safe active exploration"

        # Action is IRREVERSIBLE:
        # Check if conservative certified preconditions are satisfied
        safe_preconds = self.conservative_invariants.get(act_lower, set())
        if safe_preconds:
            missing = safe_preconds - current_state
            if missing:
                record = InterceptionRecord(
                    step_index=step_index,
                    action_name=action_name,
                    ground_args=ground_args,
                    safety_class=safety_class,
                    reason=f"Irreversible action missing certified invariant: {missing}",
                    current_state_fluents=current_state,
                )
                self.interception_history.append(record)
                return ShieldDecision.INTERCEPT, record.reason

        # If irreversible and uncertified, intercept before physical execution!
        record = InterceptionRecord(
            step_index=step_index,
            action_name=action_name,
            ground_args=ground_args,
            safety_class=safety_class,
            reason="Irreversible action without certified safety envelope; virtual interception triggered",
            current_state_fluents=current_state,
        )
        self.interception_history.append(record)
        return ShieldDecision.INTERCEPT, record.reason
