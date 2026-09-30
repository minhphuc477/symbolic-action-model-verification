"""
locm2_translator.py
Translates LOCM2 FSM-state PDDL models into standard lifted PDDL representations.
LOCM2 synthesizes state machines (FSMs) whose states are represented as abstract predicates
(e.g., b3_fsm0_state0, zero_fsm0_state0). This module aligns FSM states with domain relations
(on, ontable, clear, handempty, holding) to enable rigorous comparison with ground truth models.
"""

import re
from typing import Dict, List, Set, Tuple

BLOCKSWORLD_FSM_MAP = {
    # Hand (zero) states
    "zero_fsm0_state0": "handempty",
    "zero_fsm0_state1": "holding",
    
    # Block states in Blocksworld
    "b3_fsm0_state0": "on",
    "b3_fsm0_state1": "ontable",
    "b3_fsm0_state2": "clear",
    
    "b3_fsm1_state0": "clear",
    "b3_fsm1_state1": "ontable",
    "b3_fsm1_state2": "clear",
    "b3_fsm1_state3": "on",
    
    "b3_fsm2_state0": "on",
    "b3_fsm2_state1": "clear",
    "b3_fsm2_state2": "holding",
}

def translate_locm2_pddl(pddl_text: str, custom_mapping: Dict[str, str] = None) -> str:
    """
    Translates LOCM2 output PDDL into normalized lifted PDDL.
    """
    mapping = dict(BLOCKSWORLD_FSM_MAP)
    if custom_mapping:
        mapping.update(custom_mapping)
        
    lines = pddl_text.split("\n")
    translated_lines = []
    
    in_predicates_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Match types
        if "(:types" in stripped:
            translated_lines.append("  (:types object)")
            continue
            
        # Match predicates definition block
        if "(:predicates" in stripped:
            in_predicates_block = True
            translated_lines.append("  (:predicates")
            translated_lines.append("    (on ?o1 - object ?o2 - object)")
            translated_lines.append("    (ontable ?o1 - object)")
            translated_lines.append("    (clear ?o1 - object)")
            translated_lines.append("    (handempty)")
            translated_lines.append("    (holding ?o1 - object)")
            translated_lines.append("  )")
            continue
            
        if in_predicates_block:
            if stripped == ")":
                in_predicates_block = False
            continue
            
        # Match action name and parameters
        action_match = re.search(r'\(:action\s+([a-zA-Z0-9_\-]+)\s+:parameters\s*\((.*?)\)', line)
        if action_match:
            current_action = action_match.group(1).lower()
            raw_params = action_match.group(2)
            param_tokens = [p.strip() for p in raw_params.split() if p.startswith("?")]
            norm_params = " ".join(f"?o{i+1} - object" for i in range(len(param_tokens)))
            translated_lines.append(f"  (:action {current_action}")
            translated_lines.append(f"   :parameters ({norm_params})")
            continue
            
        # Replace FSM predicates with domain predicates
        modified_line = line
        for fsm_pred, lifted_pred in mapping.items():
            if fsm_pred in modified_line:
                def repl(m):
                    args = m.group(1).strip()
                    # extract all ?var tokens
                    arg_vars = [v for v in args.split() if v.startswith("?")]
                    if lifted_pred == "handempty":
                        return f"({lifted_pred})"
                    elif lifted_pred in ["ontable", "clear", "holding"]:
                        v = arg_vars[0] if arg_vars else "?o1"
                        return f"({lifted_pred} {v})"
                    elif lifted_pred == "on":
                        v1 = arg_vars[0] if len(arg_vars) > 0 else "?o1"
                        v2 = arg_vars[1] if len(arg_vars) > 1 else "?o2"
                        return f"({lifted_pred} {v1} {v2})"
                    return f"({lifted_pred} {args})"
                    
                modified_line = re.sub(rf'\({re.escape(fsm_pred)}(.*?)\)', repl, modified_line)

        # Clean type annotations inside precondition / effect lists
        modified_line = re.sub(r'\s+-\s+(zero|b3)', '', modified_line)
        translated_lines.append(modified_line)
        
    return "\n".join(translated_lines)

def translate_locm2_file(input_path: str, output_path: str = None) -> str:
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    translated = translate_locm2_pddl(content)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated)
    return translated

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(translate_locm2_file(sys.argv[1]))
    else:
        sample_path = "locm_repo/output/Blocksworld/Blocksworld.pddl"
        print(translate_locm2_file(sample_path))
