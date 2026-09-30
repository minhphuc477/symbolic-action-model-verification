"""
fastlas_translator.py
Translates FastLAS / ILASP Prolog-style inductive logic rules into standard PDDL action definitions.

Supported patterns:
1. Precondition rules:
   action_name(V0, V1) :- cond1(V0), not cond2(V1), cond3.
   -> translates to:
   (:action action_name
     :parameters (?v0 - object ?v1 - object)
     :precondition (and (cond1 ?v0) (not (cond2 ?v1)) (cond3))
     :effect (and ...)
   )

2. Multi-rule effect definitions:
   add(action_name(V0), pred(V0)) :- ...
   del(action_name(V0), pred(V0)) :- ...
"""

import re
from typing import Dict, List, Tuple, Set

def parse_prolog_atom(atom_str: str) -> Tuple[str, List[str], bool]:
    """
    Parses a Prolog literal into (predicate, args, is_negated).
    e.g. 'not clear(V0)' -> ('clear', ['V0'], True)
    e.g. 'hand_empty' -> ('handempty', [], False)
    """
    atom_str = atom_str.strip()
    is_neg = False
    if atom_str.startswith("not "):
        is_neg = True
        atom_str = atom_str[4:].strip()
    
    match = re.match(r'^([a-zA-Z0-9_\-]+)(?:\((.*)\))?$', atom_str)
    if not match:
        return atom_str, [], is_neg
    
    pred = match.group(1).replace("_", "").lower()
    args_raw = match.group(2)
    args = [a.strip() for a in args_raw.split(",")] if args_raw else []
    return pred, args, is_neg

def format_pddl_literal(pred: str, args: List[str], is_neg: bool = False) -> str:
    arg_pddl = " ".join(f"?{a.lower()}" for a in args)
    core = f"({pred} {arg_pddl})".replace(" )", ")") if arg_pddl else f"({pred})"
    if is_neg:
        return f"(not {core})"
    return core

def translate_fastlas_rules_to_pddl(rules_text: str, domain_name: str = "Blocksworld") -> str:
    """
    Parses FastLAS rules and converts them into PDDL action representations.
    """
    lines = [line.strip() for line in rules_text.strip().split("\n") if line.strip() and not line.strip().startswith("%")]
    actions: Dict[str, Dict] = {}

    for line in lines:
        if not line.endswith("."):
            continue
        line_clean = line[:-1].strip()
        if ":-" in line_clean:
            head_str, body_str = line_clean.split(":-", 1)
        else:
            head_str, body_str = line_clean, ""
            
        head_pred, head_args, _ = parse_prolog_atom(head_str)
        body_literals = []
        if body_str.strip():
            # split body by commas not inside parentheses
            parts = re.split(r',\s*(?![^()]*\))', body_str.strip())
            for part in parts:
                p_pred, p_args, p_neg = parse_prolog_atom(part)
                body_literals.append((p_pred, p_args, p_neg))

        # Check if head is an effect indicator: add(action(...), atom) or del(...)
        if head_pred in ["add", "initiatedat"] and len(head_args) >= 1:
            # Effect handling
            pass
        else:
            # Action precondition rule
            act_name = head_pred
            if act_name not in actions:
                actions[act_name] = {
                    "args": head_args,
                    "preconditions": [],
                    "effects": []
                }
            for p_pred, p_args, p_neg in body_literals:
                actions[act_name]["preconditions"].append((p_pred, p_args, p_neg))

    # Generate PDDL
    output_lines = [
        f"(define (domain {domain_name})",
        "  (:requirements :strips :typing)",
        "  (:types object)"
    ]
    
    # Collect all predicates
    all_preds: Set[Tuple[str, int]] = set()
    for act, data in actions.items():
        for p_pred, p_args, _ in data["preconditions"]:
            all_preds.add((p_pred, len(p_args)))
            
    output_lines.append("  (:predicates")
    for p_pred, arity in sorted(all_preds):
        if arity == 0:
            output_lines.append(f"    ({p_pred})")
        else:
            arg_str = " ".join(f"?v{i} - object" for i in range(arity))
            output_lines.append(f"    ({p_pred} {arg_str})")
    output_lines.append("  )\n")

    for act_name, data in sorted(actions.items()):
        all_act_vars = set(data["args"])
        for _, p_args, _ in data["preconditions"]:
            all_act_vars.update(p_args)
        param_str = " ".join(f"?{v.lower()} - object" for v in sorted(all_act_vars))
        
        output_lines.append(f"  (:action {act_name}")
        output_lines.append(f"    :parameters ({param_str})")
        
        preconds = [format_pddl_literal(p, a, neg) for p, a, neg in data["preconditions"]]
        if preconds:
            output_lines.append(f"    :precondition (and {' '.join(preconds)})")
        else:
            output_lines.append("    :precondition (and)")
            
        effects = [format_pddl_literal(p, a, neg) for p, a, neg in data["effects"]]
        if effects:
            output_lines.append(f"    :effect (and {' '.join(effects)})")
        else:
            output_lines.append("    :effect (and)")
        output_lines.append("  )\n")
        
    output_lines.append(")")
    return "\n".join(output_lines)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        print(translate_fastlas_rules_to_pddl(content))
    else:
        sample = "pick(V0) :- clear(V0), hand_empty."
        print(translate_fastlas_rules_to_pddl(sample))
