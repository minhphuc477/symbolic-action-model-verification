import sys
from src.adapters.locm2_translator import translate_locm2_pddl, translate_locm2_file

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "locm_repo/output/Blocksworld/Blocksworld.pddl"
    out = sys.argv[2] if len(sys.argv) > 2 else "benchmark_outputs/locm2_normalized.pddl"
    res = translate_locm2_file(inp, out)
    if len(sys.argv) <= 2:
        print(f"Translated {inp} -> {out}")
        print(res)
