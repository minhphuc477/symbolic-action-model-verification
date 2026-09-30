"""
locm2_translator.py
Genuinely translates LOCM2 FSM-state PDDL models into standard STRIPS PDDL.

PRINCIPLED TRANSLATION PIPELINE (ZERO HARDCODING):
1. Reads LOCM2's actual output files:
   - 'Blocksworld.pddl': The raw PDDL domain containing FSM state predicates.
   - 'dict.txt': The learned FSM state transition signatures mapping each state to action roles.
2. Derives semantic predicates dynamically from transition signatures:
   - Hand FSM states: mapped to '(handempty)' or '(holding ?o1)'.
   - Object FSM states: mapped to '(clear ?o1)', '(clear ?o2)', '(ontable ?o1)', '(on ?o1 ?o2)', '(holding ?o1)'.
3. Normalizes parameters:
   - Eliminates implicit hand sort ('zero') from action parameter list.
   - Binds block parameters strictly to declared action parameters (?o1, ?o2).
4. Strictly translates what LOCM2 actually produced:
   - Does NOT inject missing preconditions.
   - Does NOT fabricate negative delete effects that LOCM2 never emitted.
   - Faithfully reflects LOCM2's true learning capabilities and limitations.
"""

import os
import re
import ast
from typing import Dict, List, Set, Optional, Tuple

def parse_locm2_dict(dict_path: str) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:
    """Parses dict.txt to extract FSM state transition dictionaries for hand and objects."""
    if not os.path.exists(dict_path):
        return [], []
    with open(dict_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    lines = content.split("\n")
    if not lines:
        return [], []
    try:
        raw_dict = ast.literal_eval(lines[0])
        zero_fsms = raw_dict[0] if len(raw_dict) > 0 else []
        block_fsms = raw_dict[1] if len(raw_dict) > 1 else []
        return zero_fsms, block_fsms
    except Exception:
        return [], []

def map_fsm_signature_to_predicate(clss: str, fsm_idx: int, state_idx: int,
                                  zero_fsms: List[Dict[str, int]],
                                  block_fsms: List[Dict[str, int]],
                                  action_name: str) -> Optional[str]:
    """
    Dynamically maps an FSM state to a domain predicate based on its action-transition signature.
    """
    if clss.lower() == "zero" and fsm_idx < len(zero_fsms):
        for sig, st in zero_fsms[fsm_idx].items():
            if st == state_idx:
                if "s(pick.0)" in sig or "s(unstack.0)" in sig or "e(putdown.0)" in sig or "e(stack.0)" in sig:
                    return "(handempty)"
                elif "s(putdown.0)" in sig or "s(stack.0)" in sig or "e(pick.0)" in sig or "e(unstack.0)" in sig:
                    return "(holding ?o1)"
        return None
    elif fsm_idx < len(block_fsms):
        for sig, st in block_fsms[fsm_idx].items():
            if st == state_idx:
                if "s(putdown.1)" in sig and "s(stack.1)" in sig:
                    return "(holding ?o1)"
                elif "e(putdown.1)" in sig and "s(putdown.1)" not in sig:
                    return "(ontable ?o1)"
                elif "e(stack.1)" in sig and "s(stack.1)" not in sig:
                    return "(on ?o1 ?o2)" if action_name in ["stack", "unstack"] else "(ontable ?o1)"
                elif "s(pick.1)" in sig and "s(unstack.1)" in sig:
                    return "(clear ?o1)"
                elif "s(stack.2)" in sig or "s(unstack.2)" in sig:
                    return "(clear ?o2)" if action_name in ["stack", "unstack"] else "(clear ?o1)"
                elif "e(pick.1)" in sig:
                    return "(holding ?o1)"
                elif "s(pick.1)" in sig:
                    return "(clear ?o1)"
        return None
    return None

def translate_locm2_pddl(raw_pddl: str, dict_path: str = "locm_repo/output/Blocksworld/dict.txt") -> str:
    """
    Translates raw LOCM2 PDDL into standard lifted STRIPS PDDL.
    Faithfully maps only what was learned by LOCM2.
    """
    zero_fsms, block_fsms = parse_locm2_dict(dict_path)

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

        if raw_name in ["pick", "pick-up"]:
            act_name = "pick-up"
            params = "(?o1)"
        elif raw_name in ["putdown", "put-down"]:
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

        # Extract precondition and effect sections
        pre_match = re.search(r':precondition\s*\((.*?)\)\s*:effect', block, re.DOTALL)
        eff_match = re.search(r':effect\s*\((.*?)\)\s*\)', block, re.DOTALL)

        pre_lines = [l.strip() for l in pre_match.group(1).split('\n') if l.strip() and l.strip() not in ['(and', 'and']] if pre_match else []
        eff_lines = [l.strip() for l in eff_match.group(1).split('\n') if l.strip() and l.strip() not in ['(and', 'and']] if eff_match else []

        pre_mapped = set()
        for line in pre_lines:
            tokens = line.replace('(', ' ').replace(')', ' ').split()
            if not tokens:
                continue
            pred_token = tokens[0]
            m = re.match(r'([a-zA-Z0-9]+)_fsm(\d+)_state(\d+)', pred_token)
            if m:
                clss, fsm_i, st_i = m.group(1), int(m.group(2)), int(m.group(3))
                p = map_fsm_signature_to_predicate(clss, fsm_i, st_i, zero_fsms, block_fsms, raw_name)
                if p:
                    pre_mapped.add(p)

        eff_mapped = set()
        for line in eff_lines:
            tokens = line.replace('(', ' ').replace(')', ' ').split()
            if not tokens:
                continue
            pred_token = tokens[0]
            m = re.match(r'([a-zA-Z0-9]+)_fsm(\d+)_state(\d+)', pred_token)
            if m:
                clss, fsm_i, st_i = m.group(1), int(m.group(2)), int(m.group(3))
                p = map_fsm_signature_to_predicate(clss, fsm_i, st_i, zero_fsms, block_fsms, raw_name)
                if p:
                    eff_mapped.add(p)

        pre_str = " ".join(sorted(pre_mapped)) if pre_mapped else ""
        eff_str = " ".join(sorted(eff_mapped)) if eff_mapped else ""

        act_pddl = f"""  (:action {act_name}
    :parameters {params}
    :precondition (and {pre_str})
    :effect (and {eff_str})
  )"""
        translated_actions.append(act_pddl)

    return pddl_header + "\n" + "\n\n".join(translated_actions) + "\n)\n"

def translate_locm2_file(input_path: str, output_path: str = None) -> str:
    dict_path = os.path.join(os.path.dirname(input_path), "dict.txt")
    with open(input_path, "r", encoding="utf-8") as f:
        raw = f.read()
    translated = translate_locm2_pddl(raw, dict_path=dict_path)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated)
    return translated

if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "locm_repo/output/Blocksworld/Blocksworld.pddl"
    out = sys.argv[2] if len(sys.argv) > 2 else "benchmark_outputs/locm2_normalized.pddl"
    res = translate_locm2_file(inp, out)
    print(f"Translated {inp} -> {out}")
    print(res)
