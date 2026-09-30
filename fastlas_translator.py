import sys
from src.adapters.fastlas_translator import translate_fastlas_rules_to_pddl

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            content = f.read()
        print(translate_fastlas_rules_to_pddl(content))
    else:
        sample = "pick(V0) :- clear(V0), hand_empty."
        print(translate_fastlas_rules_to_pddl(sample))
