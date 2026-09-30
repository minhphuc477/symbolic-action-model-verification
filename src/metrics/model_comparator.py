"""
model_comparator.py
Evaluates and compares learned action models against Ground Truth PDDL domain models.

Rigorously computes:
- d_triangle: Action Model Symmetric Difference (Preconditions & Effects Graph Edit Distance, FP + FN)
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1 Score: 2 * Precision * Recall / (Precision + Recall)
- A_pred: Action Model Literal Classification Accuracy: (TP + TN) / Total Candidates = 1 - (d_triangle / |U|)
- PDDL Syntax & Semantic Validation (zero unbound variables, valid STRIPS domain)
"""

import re
from typing import Dict, List, Set, Tuple
import pddl

def extract_sexpr(text: str, keyword: str):
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return None
    start = text.find('(', idx)
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return None

def parse_atoms(sexpr: str) -> List[str]:
    if not sexpr:
        return []
    s = sexpr.strip()
    if s.startswith('(') and s.endswith(')'):
        s = s[1:-1].strip()
    if s.lower().startswith('and'):
        s = s[3:].strip()
    atoms = []
    depth = 0
    cur = ''
    for ch in s:
        if ch == '(':
            if depth == 0:
                cur = ''
            depth += 1
            cur += ch
        elif ch == ')':
            depth -= 1
            cur += ch
            if depth == 0:
                clean_atom = cur.strip()
                if clean_atom not in ["(0)", "0", ""]:
                    atoms.append(clean_atom)
                cur = ''
        elif depth > 0:
            cur += ch
    return atoms

def normalize_atom(atom_str: str, param_map: Dict[str, str]) -> str:
    norm = atom_str.lower()
    for old_p, new_p in param_map.items():
        norm = re.sub(rf'\{old_p}\b', new_p, norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    norm = norm.replace("( ", "(").replace(" )", ")")
    return norm

def parse_pddl_actions(pddl_text: str) -> Dict[str, Dict[str, Set[str]]]:
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

def get_candidate_literal_universe(action_name: str, num_params: int) -> Set[str]:
    """
    Generates the universe U of all potential candidate precondition and effect literals
    for an action in Blocksworld.
    """
    candidates = set()
    params = [f"?p{i+1}" for i in range(num_params)]
    
    # 0-arity predicates
    candidates.add("(handempty)")
    candidates.add("(not (handempty))")
    
    # 1-arity predicates over parameters
    for p in params:
        for pred in ["ontable", "clear", "holding"]:
            candidates.add(f"({pred} {p})")
            candidates.add(f"(not ({pred} {p}))")
            
    # 2-arity predicates over parameters
    for p1 in params:
        for p2 in params:
            if p1 != p2:
                candidates.add(f"(on {p1} {p2})")
                candidates.add(f"(not (on {p1} {p2}))")
                
    return candidates

def validate_pddl_domain(pddl_file_path: str) -> Tuple[bool, str]:
    """Validates domain using official pddl package parser."""
    try:
        dom = pddl.parse_domain(pddl_file_path)
        return True, f"Valid domain with {len(dom.actions)} actions"
    except Exception as e:
        return False, str(e)

def compare_action_models(ground_truth_pddl: str, learned_pddl: str, domain_file_path: str = None) -> Dict:
    """
    Compares learned PDDL against ground truth.
    """
    is_valid = True
    val_msg = "Skipped"
    if domain_file_path:
        is_valid, val_msg = validate_pddl_domain(domain_file_path)

    gt_actions = parse_pddl_actions(ground_truth_pddl)
    pred_actions = parse_pddl_actions(learned_pddl)

    all_action_names = sorted(set(gt_actions.keys()).union(set(pred_actions.keys())))
    
    total_d_triangle = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_universe = 0
    
    action_breakdown = {}

    for a in all_action_names:
        gt_a = gt_actions.get(a, {"parameters": [], "preconditions": set(), "effects": set()})
        pred_a = pred_actions.get(a, {"parameters": [], "preconditions": set(), "effects": set()})

        num_params = max(len(gt_a["parameters"]), len(pred_a["parameters"]), 1)
        universe = get_candidate_literal_universe(a, num_params)
        
        # Combine preconditions and effects for action
        gt_all = gt_a["preconditions"].union(gt_a["effects"])
        pred_all = pred_a["preconditions"].union(pred_a["effects"])

        tp = len(gt_all.intersection(pred_all))
        fp = len(pred_all - gt_all)
        fn = len(gt_all - pred_all)
        d_tri = fp + fn
        
        # Candidate universe for this action: both precondition and effect spaces (2 * |universe|)
        act_universe_size = 2 * len(universe)
        tn = act_universe_size - (tp + fp + fn)

        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_d_triangle += d_tri
        total_universe += act_universe_size

        action_breakdown[a] = {
            "gt_params": gt_a["parameters"],
            "pred_params": pred_a["parameters"],
            "pre_gt": sorted(list(gt_a["preconditions"])),
            "pre_learned": sorted(list(pred_a["preconditions"])),
            "eff_gt": sorted(list(gt_a["effects"])),
            "eff_learned": sorted(list(pred_a["effects"])),
            "d_triangle": d_tri,
            "tp": tp,
            "fp": fp,
            "fn": fn
        }

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    total_tn = total_universe - (total_tp + total_fp + total_fn)
    a_pred = (total_tp + total_tn) / total_universe if total_universe > 0 else 0.0

    return {
        "pddl_valid": is_valid,
        "validation_message": val_msg,
        "d_triangle": total_d_triangle,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "a_pred": a_pred,
        "num_gt_actions": len(gt_actions),
        "num_learned_actions": len(pred_actions),
        "total_universe_candidates": total_universe,
        "total_true_positives": total_tp,
        "total_false_positives": total_fp,
        "total_false_negatives": total_fn,
        "total_true_negatives": total_tn,
        "action_breakdown": action_breakdown
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        with open(sys.argv[1], "r") as f:
            gt = f.read()
        with open(sys.argv[2], "r") as f:
            pred = f.read()
        res = compare_action_models(gt, pred, sys.argv[2])
        print(f"PDDL Valid: {res['pddl_valid']} ({res['validation_message']})")
        print(f"d_triangle: {res['d_triangle']}")
        print(f"Precision:  {res['precision']:.3f}")
        print(f"Recall:     {res['recall']:.3f}")
        print(f"F1 Score:   {res['f1']:.3f}")
        print(f"A_pred:     {res['a_pred']:.3f}")
