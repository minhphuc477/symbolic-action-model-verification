"""
model_comparator.py
Evaluates and compares learned action models against Ground Truth PDDL domain models.
Uses robust balanced S-expression parsing for preconditions and effects.
Calculates:
- d_triangle: Action Model Symmetric Difference (Preconditions & Effects Graph Edit Distance)
- Precision, Recall, F1 score
- A_pred (Action Model Prediction Fidelity)
"""

import re
from typing import Dict, List, Set, Tuple

def extract_sexpr(text: str, keyword: str):
    """Finds keyword in text and extracts the balanced parenthesized S-expression immediately following it."""
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
    """Extracts top-level atomic formulas from an S-expression (stripping outer 'and' wrapper)."""
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
    """Normalizes whitespace, casing, and maps action variable names to canonical ?p1, ?p2..."""
    norm = atom_str.lower()
    for old_p, new_p in param_map.items():
        norm = re.sub(rf'\{old_p}\b', new_p, norm)
    # collapse duplicate spaces
    norm = re.sub(r'\s+', ' ', norm).strip()
    norm = norm.replace("( ", "(").replace(" )", ")")
    return norm

def parse_pddl_actions(pddl_text: str) -> Dict[str, Dict[str, Set[str]]]:
    """
    Parses a PDDL domain string and extracts actions with their normalized preconditions and effects.
    """
    actions = {}
    act_blocks = re.split(r'\(:action\s+', pddl_text, flags=re.I)[1:]
    
    for block in act_blocks:
        name = block.split()[0].strip().lower().replace("_", "-")
        # Action alias mapping (e.g. pick -> pick-up, putdown -> put-down)
        if name == "pick":
            name = "pick-up"
        elif name == "putdown":
            name = "put-down"

        # Parameters extraction
        param_sexpr = extract_sexpr(block, ':parameters')
        param_list = [p.strip().lower() for p in re.findall(r'\?[a-zA-Z0-9_\-]+', param_sexpr or "")]
        # Unique preserving order
        unique_params = []
        for p in param_list:
            if p not in unique_params:
                unique_params.append(p)
        param_map = {p: f"?p{i+1}" for i, p in enumerate(unique_params)}

        # Precondition extraction
        pre_sexpr = extract_sexpr(block, ':precondition')
        pre_atoms = parse_atoms(pre_sexpr)
        preconditions = set(normalize_atom(a, param_map) for a in pre_atoms)

        # Effect extraction
        eff_sexpr = extract_sexpr(block, ':effect')
        eff_atoms = parse_atoms(eff_sexpr)
        effects = set(normalize_atom(a, param_map) for a in eff_atoms)

        actions[name] = {
            "preconditions": preconditions,
            "effects": effects
        }
    return actions

def compare_action_models(ground_truth_pddl: str, learned_pddl: str) -> Dict:
    """
    Compares a learned PDDL model against the ground truth PDDL model.
    """
    gt_actions = parse_pddl_actions(ground_truth_pddl)
    pred_actions = parse_pddl_actions(learned_pddl)

    all_action_names = sorted(set(gt_actions.keys()).union(set(pred_actions.keys())))
    
    total_d_triangle = 0
    total_gt_elements = 0
    total_pred_elements = 0
    total_true_positives = 0
    
    action_breakdown = {}

    for a in all_action_names:
        gt_a = gt_actions.get(a, {"preconditions": set(), "effects": set()})
        pred_a = pred_actions.get(a, {"preconditions": set(), "effects": set()})

        # Precondition comparison
        pre_gt = gt_a["preconditions"]
        pre_pred = pred_a["preconditions"]
        pre_tp = len(pre_gt.intersection(pre_pred))
        pre_fp = len(pre_pred - pre_gt)
        pre_fn = len(pre_gt - pre_pred)
        pre_sym_diff = pre_fp + pre_fn

        # Effect comparison
        eff_gt = gt_a["effects"]
        eff_pred = pred_a["effects"]
        eff_tp = len(eff_gt.intersection(eff_pred))
        eff_fp = len(eff_pred - eff_gt)
        eff_fn = len(eff_gt - eff_pred)
        eff_sym_diff = eff_fp + eff_fn

        act_d_triangle = pre_sym_diff + eff_sym_diff
        total_d_triangle += act_d_triangle
        total_gt_elements += len(pre_gt) + len(eff_gt)
        total_pred_elements += len(pre_pred) + len(eff_pred)
        total_true_positives += pre_tp + eff_tp

        action_breakdown[a] = {
            "pre_gt": sorted(list(pre_gt)),
            "pre_learned": sorted(list(pre_pred)),
            "pre_tp": pre_tp,
            "pre_fp": pre_fp,
            "pre_fn": pre_fn,
            "eff_gt": sorted(list(eff_gt)),
            "eff_learned": sorted(list(eff_pred)),
            "eff_tp": eff_tp,
            "eff_fp": eff_fp,
            "eff_fn": eff_fn,
            "d_triangle": act_d_triangle
        }

    precision = total_true_positives / total_pred_elements if total_pred_elements > 0 else 0.0
    recall = total_true_positives / total_gt_elements if total_gt_elements > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    a_pred = recall

    return {
        "d_triangle": total_d_triangle,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "a_pred": a_pred,
        "total_gt_literals": total_gt_elements,
        "total_learned_literals": total_pred_elements,
        "total_true_positives": total_true_positives,
        "num_gt_actions": len(gt_actions),
        "num_learned_actions": len(pred_actions),
        "action_breakdown": action_breakdown
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        with open(sys.argv[1], "r") as f:
            gt = f.read()
        with open(sys.argv[2], "r") as f:
            pred = f.read()
        res = compare_action_models(gt, pred)
        print(f"d_triangle: {res['d_triangle']}")
        print(f"Precision:  {res['precision']:.3f}")
        print(f"Recall:     {res['recall']:.3f}")
        print(f"F1 Score:   {res['f1']:.3f}")
        print(f"A_pred:     {res['a_pred']:.3f}")
