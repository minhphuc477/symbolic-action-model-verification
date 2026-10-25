"""
ceg_omr_engine.py — Counterexample-Guided Online Action Model Repair
=====================================================================
Unified facade module providing backward-compatible access to the decomposed
CEG-OMR sub-components:
  * CEGOMRConfig, Counterexample, CEGOMRResult (src.repair.config)
  * FastDownwardGenerator (src.repair.generator)
  * OracleVerifier (src.repair.verifier)
  * HornSynthesizer (src.repair.horn_synthesizer)
  * CEGOMREngine (src.repair.engine)

Conforms to Algorithm 1 in thesis manuscript.
"""

from __future__ import annotations

import argparse
import sys

from src.repair.config import CEGOMRConfig, CEGOMRResult, Counterexample
from src.repair.engine import CEGOMREngine
from src.repair.generator import FastDownwardGenerator, _fd_plan_found
from src.repair.horn_synthesizer import (
    HornSynthesizer,
    _clingo_succeeded,
    _fastlas_succeeded,
)
from src.repair.verifier import OracleVerifier, _state_str
from src.utils.sexp import parse_action_tuple

# Backward compatibility alias
_parse_action_tuple = parse_action_tuple


def _parse_action_name(action_str: str) -> str:
    """Extract action name from PDDL plan action string like '(pick-up a)'."""
    action_str = action_str.strip()
    action_str = action_str.removeprefix("(")
    action_str = action_str.removesuffix(")")
    tokens = action_str.strip().split()
    return tokens[0].lower() if tokens else ""


def _cli():
    parser = argparse.ArgumentParser(description="Run CEG-OMR repair on a PDDL domain.")
    parser.add_argument("--domain", required=True, help="Path to (possibly mutated) PDDL domain")
    parser.add_argument("--problem", required=True, help="Path to PDDL problem file")
    parser.add_argument("--gt-domain", default="", help="Path to ground-truth M* domain (if different from --domain)")
    parser.add_argument("--max-iter", type=int, default=50, help="Max repair iterations")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="repair_logs/", help="Output directory")
    args = parser.parse_args()

    config = CEGOMRConfig(
        domain_path=args.domain,
        problem_path=args.problem,
        ground_truth_domain=args.gt_domain,
        max_repair_iterations=args.max_iter,
        seed=args.seed,
        out_dir=args.out,
    )
    engine = CEGOMREngine(config)
    result = engine.run()
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    _cli()

__all__ = [
    "CEGOMRConfig",
    "Counterexample",
    "CEGOMRResult",
    "FastDownwardGenerator",
    "OracleVerifier",
    "HornSynthesizer",
    "CEGOMREngine",
    "_parse_action_tuple",
    "_parse_action_name",
    "_state_str",
    "_fastlas_succeeded",
    "_clingo_succeeded",
    "_fd_plan_found",
]
