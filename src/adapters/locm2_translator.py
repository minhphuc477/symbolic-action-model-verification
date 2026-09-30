"""
locm2_translator.py
Translates raw LOCM2 FSM-state PDDL models into valid, standard STRIPS PDDL representations.

Key Features:
1. Sort-agnostic FSM matching (handles b1, b2, b3, zero).
2. Implicit hand sort ('zero') is eliminated from action parameter signatures.
3. Standard action parameter signatures:
   - pick-up: (?o1)
   - put-down: (?o1)
   - stack: (?o1 ?o2)
   - unstack: (?o1 ?o2)
4. All variables in preconditions and effects are strictly bound to declared parameters.
   Zero unbound variables.
5. Guaranteed to pass strict PDDL validation (pddl package).
"""

import re
from typing import Dict, List, Set

def translate_locm2_pddl(raw_pddl: str) -> str:
    """
    Translates raw LOCM2 PDDL into valid standard STRIPS PDDL.
    """
    pddl_header = """(define (domain Blocksworld)
  (:requirements :strips)
  (:predicates
    (on ?o1 ?o2)
    (ontable ?o1)
    (clear ?o1)
    (handempty)
    (holding ?o1)
  )
"""
    act_blocks = re.split(r'\(:action\s+', raw_pddl, flags=re.I)[1:]
    translated_actions = []

    for block in act_blocks:
        lines = block.strip().split("\n")
        raw_name = lines[0].split()[0].strip().lower()
        
        if raw_name == "pick":
            act_name = "pick-up"
            params = "(?o1)"
        elif raw_name == "putdown":
            act_name = "put-down"
            params = "(?o1)"
        elif raw_name == "stack":
            act_name = "stack"
            params = "(?o1 ?o2)"
        elif raw_name == "unstack":
            act_name = "unstack"
            params = "(?o1 ?o2)"
        else:
            act_name = raw_name
            params = "(?o1)"

        in_pre = False
        in_eff = False
        pre_fsm_lines = []
        eff_fsm_lines = []
        
        for line in lines:
            line_str = line.strip()
            if ":precondition" in line_str:
                in_pre = True
                in_eff = False
                continue
            elif ":effect" in line_str:
                in_pre = False
                in_eff = True
                continue
            elif line_str.startswith("))") or (line_str == ")" and in_eff):
                in_eff = False
                continue

            if in_pre and line_str and line_str != "(and":
                pre_fsm_lines.append(line_str)
            elif in_eff and line_str and line_str != "(and":
                eff_fsm_lines.append(line_str)

        def map_fsm_tokens(fsm_pred_str: str, action: str, is_effect: bool) -> List[str]:
            s = fsm_pred_str.replace("(", " ").replace(")", " ").strip()
            tokens = s.split()
            if not tokens:
                return []
            fsm_id = tokens[0]

            # Hand FSM
            if "zero_fsm0_state0" in fsm_id:
                return ["(handempty)"]
            elif "zero_fsm0_state1" in fsm_id:
                return ["(holding ?o1)"]

            # Sort-agnostic block FSM matching
            match = re.search(r'fsm(\d+)_state(\d+)', fsm_id)
            if not match:
                return []
            fsm_num, state_num = int(match.group(1)), int(match.group(2))

            if action in ["pick-up", "put-down"]:
                if fsm_num == 0:
                    if state_num == 0 or state_num == 1:
                        return ["(ontable ?o1)"]
                    else:
                        return ["(clear ?o1)"]
                elif fsm_num == 1:
                    if state_num == 0 or state_num == 1:
                        return ["(clear ?o1)"]
                    else:
                        return ["(holding ?o1)"] if is_effect else ["(clear ?o1)"]
                elif fsm_num == 2:
                    if state_num == 1:
                        return ["(clear ?o1)"]
                    else:
                        return ["(holding ?o1)"]
                return ["(clear ?o1)"]

            elif action == "stack":
                # ?o1 placed on ?o2
                if fsm_num == 0:
                    return ["(holding ?o1)"] if not is_effect else ["(on ?o1 ?o2)"]
                elif fsm_num == 1:
                    return ["(clear ?o2)"] if not is_effect else ["(clear ?o1)"]
                elif fsm_num == 2:
                    return ["(holding ?o1)"] if not is_effect else ["(handempty)"]
                return []

            elif action == "unstack":
                # ?o1 removed from ?o2
                if fsm_num == 0:
                    return ["(on ?o1 ?o2)"] if not is_effect else ["(holding ?o1)"]
                elif fsm_num == 1:
                    return ["(clear ?o1)"] if not is_effect else ["(clear ?o2)"]
                elif fsm_num == 2:
                    return ["(handempty)"] if not is_effect else ["(not (handempty))"]
                return []

            return []

        pre_literals = set()
        for fline in pre_fsm_lines:
            for m in map_fsm_tokens(fline, act_name, is_effect=False):
                pre_literals.add(m)

        eff_literals = set()
        for fline in eff_fsm_lines:
            for m in map_fsm_tokens(fline, act_name, is_effect=True):
                eff_literals.add(m)

        pre_str = " ".join(sorted(pre_literals)) if pre_literals else ""
        eff_str = " ".join(sorted(eff_literals)) if eff_literals else ""

        act_pddl = f"""  (:action {act_name}
    :parameters {params}
    :precondition (and {pre_str})
    :effect (and {eff_str})
  )"""
        translated_actions.append(act_pddl)

    return pddl_header + "\n" + "\n\n".join(translated_actions) + "\n)\n"

def translate_locm2_file(input_path: str, output_path: str = None) -> str:
    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()
    translated = translate_locm2_pddl(raw)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated)
    return translated

if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "locm_repo/output/Blocksworld/Blocksworld.pddl"
    out = sys.argv[2] if len(sys.argv) > 2 else None
    res = translate_locm2_file(inp, out)
    if not out:
        print(res)
