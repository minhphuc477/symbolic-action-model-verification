"""
transition_accuracy.py
Evaluates learned PDDL action models by computing real Transition Prediction Accuracy (A_pred)
over observed state transitions from genuine execution trajectories.

Definition:
A_pred = (1 / N) * sum_{i=1}^N I[ M_pred(s_i, a_i) == s_{i+1} ]
where M_pred(s_i, a_i) checks precondition applicability under the learned model,
applies the add and delete effects, and verifies set equivalence with the observed s_{i+1}.

Fixes all variable grounding bugs by strictly stripping leading '?' and applying
word-boundary regex substitutions (re.sub(rf'\\?{v}\\b', const, lit)).
"""

import os
import glob
import re
from typing import Dict, List, Set, Tuple, Optional

def safe_ground(literal: str, param_map: Dict[str, str]) -> str:
    """
    Safely grounds a PDDL literal by mapping parameters to object constants.
    Prevents double question marks (??) by stripping leading '?' from parameter keys,
    and uses word boundaries to prevent accidental partial substring replacements.
    """
    res = literal
    for var, const in param_map.items():
        v = var.lstrip('?')
        res = re.sub(rf'\?{v}\b', const, res)
    # Canonicalize spacing and parentheses
    res = re.sub(r'\s+', ' ', res.strip().lower())
    res = res.replace('( ', '(').replace(' )', ')')
    return res

def extract_sexpr(text: str, keyword: str) -> Optional[str]:
    """Extracts a balanced S-expression following a keyword."""
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

def parse_atoms(sexpr: Optional[str]) -> List[str]:
    """Parses individual atoms/literals from an S-expression."""
    if not sexpr:
        return []
    s = sexpr.strip()
    if not s.startswith('(') or not s.endswith(')'):
        return []
    inner = s[1:-1].strip()
    if inner.lower().startswith('and'):
        s = inner[3:].strip()
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
                    atom = re.sub(r'\s+', ' ', cur.strip().lower()).replace('( ', '(').replace(' )', ')')
                    if atom and atom not in ["(0)", "0"]:
                        atoms.append(atom)
                    cur = ''
            elif depth > 0:
                cur += ch
        return atoms
    else:
        atom = re.sub(r'\s+', ' ', s.strip().lower()).replace('( ', '(').replace(' )', ')')
        return [atom] if atom and atom not in ["(0)", "0"] else []

class ActionSchema:
    def __init__(self, name: str, params: List[str], preconditions: List[str], effects: List[str]):
        self.name = name.lower().replace("_", "-")
        self.params = [p.lower() for p in params]
        self.preconditions = preconditions
        self.add_effects = []
        self.del_effects = []
        
        for eff in effects:
            if eff.startswith('(not ') and eff.endswith(')'):
                self.del_effects.append(eff[5:-1].strip())
            else:
                self.add_effects.append(eff)

    def is_applicable(self, state: Set[str], param_map: Dict[str, str]) -> bool:
        for pre in self.preconditions:
            gp = safe_ground(pre, param_map)
            if gp.startswith('(not ') and gp.endswith(')'):
                pos = gp[5:-1].strip()
                if pos in state:
                    return False
            else:
                if gp not in state:
                    return False
        return True

    def apply(self, state: Set[str], param_map: Dict[str, str]) -> Optional[Set[str]]:
        if not self.is_applicable(state, param_map):
            return None
        
        next_state = set(state)
        for de in self.del_effects:
            g_del = safe_ground(de, param_map)
            next_state.discard(g_del)
        for ae in self.add_effects:
            g_add = safe_ground(ae, param_map)
            next_state.add(g_add)
            
        return next_state

def parse_pddl_model(pddl_text: str) -> Dict[str, ActionSchema]:
    """Parses a PDDL domain string into a dictionary of ActionSchema objects."""
    actions = {}
    act_blocks = re.split(r'\(:action\s+', pddl_text, flags=re.I)[1:]
    
    for block in act_blocks:
        name = block.split()[0].strip().lower().replace("_", "-")
        if name == "putdown":
            name = "put-down"

        param_sexpr = extract_sexpr(block, ':parameters')
        params = re.findall(r'\?[a-zA-Z0-9_\-]+', param_sexpr or '')
        
        pre_sexpr = extract_sexpr(block, ':precondition')
        pre = parse_atoms(pre_sexpr)
        
        eff_sexpr = extract_sexpr(block, ':effect')
        eff = parse_atoms(eff_sexpr)
        
        schema = ActionSchema(name, params, pre, eff)
        actions[name] = schema
        if name == "pick":
            actions["pick-up"] = schema
        elif name == "pick-up":
            actions["pick"] = schema
        
    return actions

def load_trajectories(dataset_dir: str) -> List[Tuple[Set[str], str, List[str], Set[str]]]:
    """
    Loads all transitions (s_t, action_name, action_args, s_{t+1}) from trajectory files.
    """
    pattern = os.path.join(dataset_dir, "trajectory-*")
    traj_files = sorted(glob.glob(pattern))
    transitions = []

    for fpath in traj_files:
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        init_match = re.search(r'\(:init\s+(.*?)\)\s*\(:action', text, re.DOTALL)
        if not init_match:
            continue
        cur_state = set(parse_atoms(f'(and {init_match.group(1)})'))

        parts = re.findall(r'\(:action\s+\((.*?)\)\)\s*\(:state\s+(.*?)\)\s*(?=\(:action|\)\s*$)', text, re.DOTALL)
        for act_str, state_str in parts:
            act_tokens = act_str.strip().split()
            act_name = act_tokens[0].lower().replace("_", "-")
            if act_name == "pick":
                act_name = "pick-up"
            elif act_name == "putdown":
                act_name = "put-down"
            act_args = [a.lower() for a in act_tokens[1:]]
            obs_next = set(parse_atoms(f'(and {state_str})'))
            
            transitions.append((cur_state, act_name, act_args, obs_next))
            cur_state = obs_next

    return transitions

def evaluate_transition_accuracy(pddl_text: str, dataset_dir: str = "daineto-meta-planning/src/meta_planning/dataset/blocks") -> Dict:
    """
    Calculates genuine transition prediction accuracy (A_pred) over all real transitions.
    """
    model = parse_pddl_model(pddl_text)
    transitions = load_trajectories(dataset_dir)
    total = len(transitions)
    
    if total == 0:
        return {"a_pred": 0.0, "total_transitions": 0, "correct_transitions": 0}

    correct = 0
    applicable_count = 0
    per_action_stats = {}

    for cur_state, act_name, act_args, obs_next in transitions:
        if act_name not in per_action_stats:
            per_action_stats[act_name] = {"total": 0, "correct": 0, "applicable": 0}
        per_action_stats[act_name]["total"] += 1

        if act_name not in model:
            # Action not learned in model
            continue

        schema = model[act_name]
        param_map = {p: a for p, a in zip(schema.params, act_args)}
        
        is_appl = schema.is_applicable(cur_state, param_map)
        if is_appl:
            applicable_count += 1
            per_action_stats[act_name]["applicable"] += 1
            
        pred_next = schema.apply(cur_state, param_map)
        if pred_next is not None and pred_next == obs_next:
            correct += 1
            per_action_stats[act_name]["correct"] += 1

    a_pred = correct / total
    a_appl = applicable_count / total

    return {
        "a_pred": a_pred,
        "a_appl": a_appl,
        "total_transitions": total,
        "correct_transitions": correct,
        "applicable_transitions": applicable_count,
        "per_action_stats": per_action_stats
    }

if __name__ == "__main__":
    import sys
    pddl_file = sys.argv[1] if len(sys.argv) > 1 else "benchmark_outputs/ground_truth.pddl"
    with open(pddl_file, "r", encoding="utf-8") as f:
        text = f.read()
    res = evaluate_transition_accuracy(text)
    print(f"Results for {pddl_file}:")
    print(f"  Total Transitions: {res['total_transitions']}")
    print(f"  A_pred: {res['a_pred']:.4f} ({res['correct_transitions']}/{res['total_transitions']})")
    print(f"  A_appl: {res['a_appl']:.4f} ({res['applicable_transitions']}/{res['total_transitions']})")
    for act, st in res['per_action_stats'].items():
        print(f"    - {act:<10}: {st['correct']}/{st['total']} correct (appl: {st['applicable']}/{st['total']})")
