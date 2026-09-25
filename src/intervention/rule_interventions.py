"""
AST Rule Intervention Engine with Clean Strategy Pattern
Applies 10-level AST rule interventions (Type I to Type X) following SOLID principles.
"""

from abc import ABC, abstractmethod
import copy
import random
from typing import Dict, Any, List, Optional
from enum import Enum

class InterventionType(Enum):
    TYPE_I = "Type_I_OmitLeafPrecondition"
    TYPE_II = "Type_II_OmitBottleneckPrecondition"
    TYPE_III = "Type_III_RedundantEffectAddition"
    TYPE_IV = "Type_IV_InvertBufferCondition"
    TYPE_V = "Type_V_GlobalPhaseShift"
    TYPE_VI = "Type_VI_RenameVariableAttribute"
    TYPE_VII = "Type_VII_SwapLHSConditionOrder"
    TYPE_VIII = "Type_VIII_MutateGridParams"
    TYPE_IX = "Type_IX_OmitGoalCheckPredicate"
    TYPE_X = "Type_X_Combinatorial3ASTMutations"

class BaseInterventionStrategy(ABC):
    """Abstract Base Class for AST Rule Intervention Strategies."""
    
    @abstractmethod
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        pass

class OmitLeafPreconditionStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            precs = actions[target_act].get("preconditions", [])
            if precs:
                actions[target_act]["preconditions"].pop(0)
        return M

class OmitBottleneckPreconditionStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act]["preconditions"] = [
                p for p in actions[target_act].get("preconditions", []) 
                if "critical" not in p and "door" not in p
            ]
        return M

class RedundantEffectStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].setdefault("add_effects", []).append("(redundant_flag_set)")
        return M

class InvertBufferConditionStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].setdefault("preconditions", []).append("(not (is_buffer_full))")
        return M

class GlobalPhaseShiftStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        for act in M.get("actions", {}).values():
            act["add_effects"], act["delete_effects"] = act.get("delete_effects", []), act.get("add_effects", [])
        return M

class RenameVariableAttributeStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].setdefault("preconditions", []).append("(renamed_attr ?x)")
        return M

class SwapLHSConditionOrderStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].get("preconditions", []).reverse()
        return M

class MutateGridParamsStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].setdefault("preconditions", []).append("(grid_step_offset_2)")
        return M

class OmitGoalCheckPredicateStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act]["preconditions"] = [
                p for p in actions[target_act].get("preconditions", []) 
                if "goal" not in p
            ]
        return M

class Combinatorial3ASTMutationsStrategy(BaseInterventionStrategy):
    def apply(self, model_dict: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if actions:
            target_act = rng.choice(list(actions.keys()))
            actions[target_act].setdefault("preconditions", []).append("(combo_mut_1)")
            actions[target_act].setdefault("add_effects", []).append("(combo_mut_2)")
            actions[target_act].setdefault("delete_effects", []).append("(combo_mut_3)")
        return M

class RuleInterventionEngine:
    """Engine mapping intervention requests to specific AST strategy handlers."""
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self._strategies: Dict[str, BaseInterventionStrategy] = {
            InterventionType.TYPE_I.value: OmitLeafPreconditionStrategy(),
            "Type_I": OmitLeafPreconditionStrategy(),
            InterventionType.TYPE_II.value: OmitBottleneckPreconditionStrategy(),
            "Type_II": OmitBottleneckPreconditionStrategy(),
            InterventionType.TYPE_III.value: RedundantEffectStrategy(),
            "Type_III": RedundantEffectStrategy(),
            InterventionType.TYPE_IV.value: InvertBufferConditionStrategy(),
            "Type_IV": InvertBufferConditionStrategy(),
            InterventionType.TYPE_V.value: GlobalPhaseShiftStrategy(),
            "Type_V": GlobalPhaseShiftStrategy(),
            InterventionType.TYPE_VI.value: RenameVariableAttributeStrategy(),
            "Type_VI": RenameVariableAttributeStrategy(),
            InterventionType.TYPE_VII.value: SwapLHSConditionOrderStrategy(),
            "Type_VII": SwapLHSConditionOrderStrategy(),
            InterventionType.TYPE_VIII.value: MutateGridParamsStrategy(),
            "Type_VIII": MutateGridParamsStrategy(),
            InterventionType.TYPE_IX.value: OmitGoalCheckPredicateStrategy(),
            "Type_IX": OmitGoalCheckPredicateStrategy(),
            InterventionType.TYPE_X.value: Combinatorial3ASTMutationsStrategy(),
            "Type_X": Combinatorial3ASTMutationsStrategy(),
        }

    def register_strategy(self, type_key: str, strategy: BaseInterventionStrategy) -> None:
        """Allows dynamic extension of new AST intervention strategies (Open/Closed Principle)."""
        self._strategies[type_key] = strategy

    def apply_intervention(self, model_dict: Dict[str, Any], intervention_type: str, delta_dsl: int = 1) -> Dict[str, Any]:
        """Dispatches AST intervention request to registered strategy handler."""
        strategy = self._strategies.get(intervention_type)
        if not strategy:
            raise ValueError(f"Unknown intervention type: {intervention_type}")
        return strategy.apply(model_dict, self.rng)

if __name__ == "__main__":
    import json
    engine = RuleInterventionEngine()
    sample_model = {
        "actions": {
            "move": {
                "preconditions": ["(at player pos1)", "(not (is-wall pos2))"],
                "add_effects": ["(at player pos2)"],
                "delete_effects": ["(at player pos1)"]
            }
        }
    }
    intervened = engine.apply_intervention(sample_model, "Type_II")
    print("=== Refactored Rule Intervention Engine Verification ===")
    print(json.dumps(intervened, indent=2))
