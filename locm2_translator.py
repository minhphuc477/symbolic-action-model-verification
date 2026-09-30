import sys
from src.adapters.locm2_translator import translate_locm2_pddl, translate_locm2_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        res = translate_locm2_file(inp, out)
        if not out:
            print(res)
    else:
        inp = "locm_repo/output/Blocksworld/Blocksworld.pddl"
        out = "benchmark_outputs/locm2_normalized.pddl"
        print(f"Translating {inp} -> {out}")
        translate_locm2_file(inp, out)
