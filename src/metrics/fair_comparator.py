"""
fair_comparator.py
Fair, multi-faceted comparison of action model learners:
1. Distinguishes Precondition-only learners (e.g. FastLAS) from Full-model learners (e.g. FAMA, LOCM2).
2. Computes granular metrics:
   - For FastLAS (Precondition-only):
     * Precondition Precision, Recall, F1
     * Applicability Accuracy (A_appl)
     * Transition Accuracy (A_pred) is NOT evaluated (marked as N/A).
   - For FAMA & LOCM2 (Full-model learners):
     * Precondition Precision, Recall, F1
     * Effect Precision, Recall, F1
     * Action Model Symmetric Difference d_triangle (FP + FN)
     * Empirical State Transition Accuracy (A_pred) over real execution trajectories
     * Applicability Accuracy (A_appl)
3. Evaluates syntax and STRIPS validity via official pddl parser.
"""

import os
import sys
import re
from typing import Dict, List, Set, Tuple, Optional

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pddl
from src.metrics.transition_accuracy import evaluate_transition_accuracy, safe_ground, extract_sexpr, parse_atoms

def normalize_atom(atom_str: str, param_map: Dict[str, str]) -> str:
    """Normalizes atom by mapping parameters to canonical ?p1, ?p2... without ? bugs."""
    norm = atom_str.lower()
    for old_p, new_p in param_map.items():
        v = old_p.lstrip('?')
        norm = re.sub(rf'\?{v}\b', new_p, norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    norm = norm.replace("( ", "(").replace(" )", ")")
    return norm

def parse_pddl_schemas(pddl_text: str) -> Dict[str, Dict[str, Set[str]]]:
    """Parses PDDL actions into canonical parameter-normalized preconditions and effects."""
    actions = {}
    act_blocks = re.split(r'\(:action\s+', pddl_text, flags=re.I)[1:]

    for block in act_blocks:
        name = block.split()[0].strip().lower().replace("_", "-")
        if name == "pick":
            name = "pick-up"
        elif name == "putdown":
            name = "put-down"

        param_sexpr = extract_sexpr(block, ':parameters')
        param_list = [p.strip().lower() for p in re.findall(r'\?[a-zA-Z0-9_\-]+', param_sexpr or "")]
        unique_params = []
        for p in param_list:
            if p not in unique_params:
                unique_params.append(p)
        param_map = {p: f"?p{i+1}" for i, p in enumerate(unique_params)}

        pre_sexpr = extract_sexpr(block, ':precondition')
        pre_atoms = parse_atoms(pre_sexpr)
        preconditions = set(normalize_atom(a, param_map) for a in pre_atoms)

        eff_sexpr = extract_sexpr(block, ':effect')
        eff_atoms = parse_atoms(eff_sexpr)
        effects = set(normalize_atom(a, param_map) for a in eff_atoms)

        actions[name] = {
            "parameters": [f"?p{i+1}" for i in range(len(unique_params))],
            "preconditions": preconditions,
            "effects": effects
        }
    return actions

def compute_prf(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if fn == 0 else 0.0)
    r = tp / (tp + fn) if (tp + fn) > 0 else (1.0 if fp == 0 else 0.0)
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1

def compare_fairly(gt_pddl: str, learned_pddl: str, pddl_filepath: Optional[str] = None, learner_type: str = "full") -> Dict:
    """
    Rigorously compares a learned PDDL model against ground truth across both structural
    and empirical behavioral dimensions.
    """
    is_valid = True
    val_msg = "Skipped"
    if pddl_filepath and os.path.exists(pddl_filepath):
        try:
            dom = pddl.parse_domain(pddl_filepath)
            is_valid = True
            val_msg = f"Valid domain with {len(dom.actions)} actions"
        except Exception as e:
            is_valid = False
            val_msg = str(e)

    gt_actions = parse_pddl_schemas(gt_pddl)
    learned_actions = parse_pddl_schemas(learned_pddl)

    all_actions = sorted(set(gt_actions.keys()).union(set(learned_actions.keys())))
    is_pre_only = "precondition" in learner_type.lower()

    # Precondition aggregates
    pre_tp = pre_fp = pre_fn = 0
    # Effect aggregates
    eff_tp = eff_fp = eff_fn = 0
    total_d_triangle = 0

    per_action_breakdown = {}

    for a in all_actions:
        gt_a = gt_actions.get(a, {"preconditions": set(), "effects": set()})
        lrn_a = learned_actions.get(a, {"preconditions": set(), "effects": set()})

        # Preconditions
        p_tp = len(gt_a["preconditions"].intersection(lrn_a["preconditions"]))
        p_fp = len(lrn_a["preconditions"] - gt_a["preconditions"])
        p_fn = len(gt_a["preconditions"] - lrn_a["preconditions"])
        p_prec, p_rec, p_f1 = compute_prf(p_tp, p_fp, p_fn)

        pre_tp += p_tp
        pre_fp += p_fp
        pre_fn += p_fn

        # Effects (evaluated only if not precondition-only learner)
        e_tp = len(gt_a["effects"].intersection(lrn_a["effects"]))
        e_fp = len(lrn_a["effects"] - gt_a["effects"])
        e_fn = len(gt_a["effects"] - lrn_a["effects"])
        e_prec, e_rec, e_f1 = compute_prf(e_tp, e_fp, e_fn)

        eff_tp += e_tp
        eff_fp += e_fp
        eff_fn += e_fn

        if is_pre_only:
            act_d_tri = p_fp + p_fn
        else:
            act_d_tri = (p_fp + p_fn) + (e_fp + e_fn)
            
        total_d_triangle += act_d_tri

        per_action_breakdown[a] = {
            "preconditions": {
                "gt": sorted(list(gt_a["preconditions"])),
                "learned": sorted(list(lrn_a["preconditions"])),
                "precision": p_prec,
                "recall": p_rec,
                "f1": p_f1,
                "tp": p_tp, "fp": p_fp, "fn": p_fn
            },
            "effects": {
                "gt": sorted(list(gt_a["effects"])),
                "learned": sorted(list(lrn_a["effects"])),
                "precision": e_prec if not is_pre_only else None,
                "recall": e_rec if not is_pre_only else None,
                "f1": e_f1 if not is_pre_only else None,
                "tp": e_tp, "fp": e_fp, "fn": e_fn
            },
            "d_triangle": act_d_tri
        }

    overall_pre_p, overall_pre_r, overall_pre_f1 = compute_prf(pre_tp, pre_fp, pre_fn)
    overall_eff_p, overall_eff_r, overall_eff_f1 = compute_prf(eff_tp, eff_fp, eff_fn)

    # Empirical transition accuracy over real execution dataset
    trans_eval = evaluate_transition_accuracy(learned_pddl)

    return {
        "learner_type": learner_type,
        "is_precondition_only": is_pre_only,
        "pddl_valid": is_valid,
        "validation_message": val_msg,
        "num_gt_actions": len(gt_actions),
        "num_learned_actions": len(learned_actions),
        "d_triangle": total_d_triangle,
        "preconditions": {
            "precision": overall_pre_p,
            "recall": overall_pre_r,
            "f1": overall_pre_f1,
            "tp": pre_tp, "fp": pre_fp, "fn": pre_fn
        },
        "effects": {
            "precision": overall_eff_p if not is_pre_only else None,
            "recall": overall_eff_r if not is_pre_only else None,
            "f1": overall_eff_f1 if not is_pre_only else None,
            "tp": eff_tp, "fp": eff_fp, "fn": eff_fn
        },
        "transition_evaluation": trans_eval if not is_pre_only else None,
        "a_pred": trans_eval["a_pred"] if not is_pre_only else None,
        "a_appl": trans_eval["a_appl"],
        "action_breakdown": per_action_breakdown
    }
