import sys
from src.adapters.fama_cleaner import clean_fama_file, clean_fama_pddl

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        res = clean_fama_file(inp, out)
        if not out:
            print(res)
    else:
        print("Usage: python fama_cleaner.py <input_fama_pddl> [output_file]")
