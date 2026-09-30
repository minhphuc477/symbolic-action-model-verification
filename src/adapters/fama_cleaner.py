"""
fama_cleaner.py
Cleans artifacts from FAMA / Madagascar SAT planner PDDL output:
1. Strips trailing '0' artifact literals in effect blocks.
2. Strips redundant '(:types object)' and '- object' parameter annotations to conform
   strictly to standard STRIPS PDDL and pass strict PDDL validators.
"""

import re
import sys

def clean_fama_pddl(pddl_text: str) -> str:
    """
    Removes artifact '0' tokens from action effect blocks and normalizes types in FAMA learned PDDL.
    """
    # Remove lines containing only '0' or whitespace with '0'
    cleaned = re.sub(r'^\s*0\s*$', '', pddl_text, flags=re.MULTILINE)
    # Remove standalone '0' inside parenthesized expressions: e.g. '(and ... 0)' -> '(and ...)'
    cleaned = re.sub(r'\s+0\s*(?=\))', '', cleaned)
    # Remove (:types object) keyword conflict for PDDL validators
    cleaned = re.sub(r'\(:types\s+object\s*\)', '', cleaned, flags=re.IGNORECASE)
    # Remove '- object' typing from parameters
    cleaned = re.sub(r'\s+-\s+object\b', '', cleaned, flags=re.IGNORECASE)
    # Remove multiple consecutive blank lines
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    return cleaned.strip() + "\n"

def clean_fama_file(input_path: str, output_path: str = None) -> str:
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = clean_fama_pddl(content)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
    return cleaned

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        result = clean_fama_file(inp, out)
        if not out:
            print(result)
    else:
        print("Usage: python fama_cleaner.py <input_pddl_file> [output_pddl_file]")
