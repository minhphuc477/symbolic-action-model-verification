"""
AST Rule Intervention Engine
Applies 5-level AST rule interventions (Type I - Micro Shift, Type II - Latent Counter, Type III - Disjunctive Condition, Type IV - Spatial Coupling, Type V - Global Phase Shift) to ground-truth action models.
"""

import copy
import random
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

class RuleInterventionEngine:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def apply_intervention(self, model_dict, intervention_type, delta_dsl=1):
        """
        Applies requested 10-level AST rule intervention to ground-truth model.
        """
        M = copy.deepcopy(model_dict)
        actions = M.get("actions", {})
        if not actions:
            return M
            
        action_names = list(actions.keys())
        target_act = self.rng.choice(action_names)
        
        if intervention_type in [InterventionType.TYPE_I.value, "Type_I"]:
            # Type I: Omit leaf precondition (delta_dsl = 1)
            precs = actions[target_act].get("preconditions", [])
            if precs:
                actions[target_act]["preconditions"].pop(0)
                
        elif intervention_type in [InterventionType.TYPE_II.value, "Type_II"]:
            # Type II: Omit bottleneck precondition (delta_dsl = 1)
            actions[target_act]["preconditions"] = [p for p in actions[target_act].get("preconditions", []) if "critical" not in p and "door" not in p]
            
        elif intervention_type in [InterventionType.TYPE_III.value, "Type_III"]:
            # Type III: Redundant effect addition (delta_dsl = 1)
            actions[target_act]["add_effects"].append("(redundant_flag_set)")
            
        elif intervention_type in [InterventionType.TYPE_IV.value, "Type_IV"]:
            # Type IV: Invert buffer condition (delta_dsl = 2)
            actions[target_act]["preconditions"].append("(not (is_buffer_full))")
            
        elif intervention_type in [InterventionType.TYPE_V.value, "Type_V"]:
            # Type V: Global phase shift (delta_dsl = 3)
            for act in actions.values():
                act["add_effects"], act["delete_effects"] = act.get("delete_effects", []), act.get("add_effects", [])
                
        elif intervention_type in [InterventionType.TYPE_VI.value, "Type_VI"]:
            # Type VI: Rename variable attribute (delta_dsl = 1)
            actions[target_act]["preconditions"].append("(renamed_attr ?x)")
            
        elif intervention_type in [InterventionType.TYPE_VII.value, "Type_VII"]:
            # Type VII: Swap LHS condition order (delta_dsl = 2)
            actions[target_act]["preconditions"].reverse()
            
        elif intervention_type in [InterventionType.TYPE_VIII.value, "Type_VIII"]:
            # Type VIII: Mutate 2D grid parameters (delta_dsl = 2)
            actions[target_act]["preconditions"].append("(grid_step_offset_2)")
            
        elif intervention_type in [InterventionType.TYPE_IX.value, "Type_IX"]:
            # Type IX: Omit goal check predicate (delta_dsl = 4)
            actions[target_act]["preconditions"] = [p for p in actions[target_act].get("preconditions", []) if "goal" not in p]
            
        elif intervention_type in [InterventionType.TYPE_X.value, "Type_X"]:
            # Type X: Combinatorial 3 AST mutations (delta_dsl = 5)
            actions[target_act]["preconditions"].append("(combo_mut_1)")
            actions[target_act]["add_effects"].append("(combo_mut_2)")
            actions[target_act]["delete_effects"].append("(combo_mut_3)")
                
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
