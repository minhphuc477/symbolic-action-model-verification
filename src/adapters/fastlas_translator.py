"""
fastlas_translator.py
Translates FastLAS / ILASP Prolog-style inductive logic rules into standard PDDL action definitions.

Converts:
unstack(V0,V1) :- clear(V0), handempty, on(V0,V1).
->
(:action unstack
  :parameters (?o1 ?o2)
  :precondition (and (clear ?o1) (handempty) (on ?o1 ?o2))
  :effect (and)
)
"""

import re


def parse_prolog_atom(atom_str: str) -> tuple[str, list[str], bool]:
    """
    Parses a Prolog literal into (predicate, args, is_negated).
    e.g. 'not clear(V0)' -> ('clear', ['V0'], True)
    e.g. 'handempty' -> ('handempty', [], False)
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

def format_pddl_literal(pred: str, args: list[str], is_neg: bool = False) -> str:
    arg_pddl = " ".join(f"?{a.lower()}" for a in args)
    core = f"({pred} {arg_pddl})".replace(" )", ")") if arg_pddl else f"({pred})"
    if is_neg:
        return f"(not {core})"
    return core

def translate_fastlas_rules_to_pddl(rules_text: str, domain_name: str = "Blocksworld") -> str:
    """
    Parses FastLAS rules and converts them into standard STRIPS PDDL action representations.
    """
    lines = [line.strip() for line in rules_text.strip().split("\n") if line.strip() and not line.strip().startswith("%")]
    actions: dict[str, dict] = {}

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
            parts = re.split(r',\s*(?![^()]*\))', body_str.strip())
            for part in parts:
                p_pred, p_args, p_neg = parse_prolog_atom(part)
                body_literals.append((p_pred, p_args, p_neg))

        # Action name normalization
        act_name = head_pred.lower().replace("_", "-")
        if act_name == "pick":
            act_name = "pick-up"
        elif act_name == "putdown":
            act_name = "put-down"

        # Canonical parameter mapping: V0 -> o1, V1 -> o2
        param_map = {f"v{i}": f"o{i+1}" for i in range(len(head_args))}
        mapped_head_args = [param_map.get(a.lower(), a.lower()) for a in head_args]

        mapped_preconds = []
        for p_pred, p_args, p_neg in body_literals:
            mapped_p_args = [param_map.get(a.lower(), a.lower()) for a in p_args]
            mapped_preconds.append((p_pred, mapped_p_args, p_neg))

        if act_name not in actions:
            actions[act_name] = {
                "args": mapped_head_args,
                "preconditions": [],
                "effects": []
            }
        for p in mapped_preconds:
            if p not in actions[act_name]["preconditions"]:
                actions[act_name]["preconditions"].append(p)

    output_lines = [
        f"(define (domain {domain_name})",
        "  (:requirements :strips)",
        "  (:predicates",
        "    (on ?o1 ?o2)",
        "    (ontable ?o1)",
        "    (clear ?o1)",
        "    (handempty)",
        "    (holding ?o1)",
        "  )\n"
    ]

    for act_name in sorted(actions.keys()):
        data = actions[act_name]
        param_str = " ".join(f"?{v}" for v in data["args"])
        
        output_lines.append(f"  (:action {act_name}")
        output_lines.append(f"    :parameters ({param_str})")
        
        preconds = [format_pddl_literal(p, a, neg) for p, a, neg in data["preconditions"]]
        if preconds:
            output_lines.append(f"    :precondition (and {' '.join(sorted(preconds))})")
        else:
            output_lines.append("    :precondition (and)")
            
        effects = [format_pddl_literal(p, a, neg) for p, a, neg in data["effects"]]
        if effects:
            output_lines.append(f"    :effect (and {' '.join(sorted(effects))})")
        else:
            output_lines.append("    :effect (and)")
        output_lines.append("  )\n")
        
    output_lines.append(")\n")
    return "\n".join(output_lines)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        print(translate_fastlas_rules_to_pddl(content))
    else:
        sample = "pick(V0) :- clear(V0), ontable(V0), handempty."
        print(translate_fastlas_rules_to_pddl(sample))
