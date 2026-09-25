"""
AST Rule Intervention Engine
Applies 5-level AST rule interventions (Type I - Micro Shift, Type II - Latent Counter, Type III - Disjunctive Condition, Type IV - Spatial Coupling, Type V - Global Phase Shift) to ground-truth action models.
"""

import copy
import random
from enum import Enum

class InterventionType(Enum):
    TYPE_I = "Type_I_MicroLocalShift"
    TYPE_II = "Type_II_LatentCounter"
    TYPE_III = "Type_III_DisjunctiveCondition"
    TYPE_IV = "Type_IV_SpatialCoupling"
    TYPE_V = "Type_V_GlobalPhaseShift"

class RuleInterventionEngine:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def apply_intervention(self, model_dict, intervention_type, delta_dsl=1):
        """
        Applies requested AST rule intervention to ground-truth model.
        """
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if not actions:
            return M
            
        action_names = list(actions.keys())
        target_act = self.rng.choice(action_names)
        
        if intervention_type == InterventionType.TYPE_I.value or intervention_type == "Type_I":
            # Micro Local Shift: remove 1 precondition
            precs = actions[target_act].get("preconditions", [])
            if precs:
                removed = self.rng.choice(precs)
                actions[target_act]["preconditions"].remove(removed)
                
        elif intervention_type == InterventionType.TYPE_II.value or intervention_type == "Type_II":
            # Latent Counter: add unobservable counter predicate
            actions[target_act]["preconditions"].append("(latent_counter_val ?x)")
            
        elif intervention_type == InterventionType.TYPE_III.value or intervention_type == "Type_III":
            # Disjunctive Condition: convert single condition to disjunction
            actions[target_act]["preconditions"].append("(or (is-active ?x) (is-override ?x))")
            
        elif intervention_type == InterventionType.TYPE_IV.value or intervention_type == "Type_IV":
            # Spatial Coupling: add non-local spatial coupling precondition
            actions[target_act]["preconditions"].append("(coupled_remote_cell ?loc1 ?loc2)")
            
        elif intervention_type == InterventionType.TYPE_V.value or intervention_type == "Type_V":
            # Global Phase Shift: swap add and delete effects across all actions
            for act in actions.values():
                act["add_effects"], act["delete_effects"] = act.get("delete_effects", []), act.get("add_effects", [])
                
        return M

if __name__ == "__main__":
    engine = RuleInterventionEngine()
    sample_model = {
        "actions": {
            "move": {"preconditions": ["(at player pos1)", "(not (is-wall pos2))"], "add_effects": ["(at player pos2)"], "delete_effects": ["(at player pos1)"]}
        }
    }
    intervened = engine.apply_intervention(sample_model, "Type_II")
    print("=== Rule Intervention Engine Verification ===")
    print(json.dumps(intervened, indent=2))
