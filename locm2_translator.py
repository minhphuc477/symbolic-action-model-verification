import sys
from src.adapters.locm2_translator import translate_locm2_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        out = sys.argv[2] if len(sys.argv) > 2 else None
        print(translate_locm2_file(sys.argv[1], out))
    else:
        sample_path = "locm_repo/output/Blocksworld/Blocksworld.pddl"
        print(translate_locm2_file(sample_path))
