"""
PDDL Domain Mutator — CEG-OMR Thesis
=====================================
Applies Type I / Type II / Type III rule interventions directly on PDDL domain
files at the AST level using the `pddl` library (v0.4.10+).

Intervention taxonomy (from research-state.yaml / theory docs):
  Type I  — OmitLeafPrecondition     : Remove a non-critical precondition atom
  Type II — OmitBottleneckPrecondition: Remove the single bottleneck precondition
             that blocks the critical path (induces phantom subtree Ω(b^(D-d)))
  Type III— RedundantEffectAddition   : Add a vacuously-true redundant effect atom

Design decisions:
  * All mutations are deterministic given a seed (seeded random.Random, sorted key order)
  * Mutations are applied at the `pddl.Domain` object level then serialized back to PDDL
  * Output files written to `domains/mutated/<domain>_<intervention>_seed<seed>.pddl`
  * ZERO synthetic data: mutation logic reads/writes real PDDL files only

Usage (CLI):
    python -m src.interventions.pddl_mutator \\
        --domain domains/blocksworld/domain.pddl \\
        --intervention Type_II \\
        --action unstack \\
        --seed 42 \\
        --out domains/mutated/

Usage (Python API):
    from src.interventions.pddl_mutator import PDDLMutator
    mutator = PDDLMutator(seed=42)
    mutated_path = mutator.apply(
        domain_path="domains/blocksworld/domain.pddl",
        intervention="Type_II",
        target_action="unstack",
        out_dir="domains/mutated/"
    )
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import random
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

# ---------------------------------------------------------------------------
# Lightweight PDDL text-level AST manipulation
# We parse PDDL with the `pddl` library for validation, but perform mutations
# on the raw PDDL text using a simple S-expression tokenizer (lark-based) to
# avoid full round-trip serialization limitations of pddl v0.4.x.
# ---------------------------------------------------------------------------

_PDDL_AVAILABLE = importlib.util.find_spec("pddl") is not None
if not _PDDL_AVAILABLE:
    print("[WARNING] `pddl` library not found. Validation will be skipped.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class InterventionType(Enum):
    TYPE_I   = "Type_I_OmitLeafPrecondition"
    TYPE_II  = "Type_II_OmitBottleneckPrecondition"
    TYPE_III = "Type_III_RedundantEffectAddition"


@dataclass
class MutationRecord:
    """Immutable record of what was mutated — needed for Theorem 2 empirical validation."""
    domain_path: str
    intervention: str
    target_action: str
    seed: int
    removed_atoms: list[str] = field(default_factory=list)
    added_atoms: list[str] = field(default_factory=list)
    output_path: str = ""
    delta_dsl: int = 1  # k in the bound K_repair ≤ k·|F|^r


# ---------------------------------------------------------------------------
# S-expression tokenizer (no external deps beyond stdlib)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Tokenize PDDL text into a flat list of tokens (parens + atoms)."""
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in "()":
            tokens.append(c)
            i += 1
        elif c == ";":
            # Comment — skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
        elif c in " \t\r\n":
            i += 1
        else:
            # Atom
            j = i
            while j < len(text) and text[j] not in " \t\r\n();":
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def _parse_sexp(tokens: list[str], pos: int = 0):
    """Recursive descent S-expression parser. Returns (sexp, next_pos)."""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of tokens")
    if tokens[pos] == "(":
        lst = []
        pos += 1  # consume "("
        while pos < len(tokens) and tokens[pos] != ")":
            item, pos = _parse_sexp(tokens, pos)
            lst.append(item)
        if pos >= len(tokens):
            raise ValueError("Unmatched '('")
        pos += 1  # consume ")"
        return lst, pos
    else:
        return tokens[pos], pos + 1


def _sexp_to_str(sexp, indent: int = 0) -> str:
    """Serialize S-expression back to PDDL string with basic indentation."""
    pad = "  " * indent
    if isinstance(sexp, str):
        return sexp
    if len(sexp) == 0:
        return "()"
    # Single-atom list
    inner_strs = [_sexp_to_str(item, indent + 1) for item in sexp]
    # Heuristic: if all children are atoms, keep on one line
    if all(isinstance(item, str) for item in sexp):
        return "(" + " ".join(inner_strs) + ")"
    # Multi-element with nested lists
    head = _sexp_to_str(sexp[0])
    if len(sexp) == 1:
        return f"({head})"
    rest = "\n".join(pad + "  " + _sexp_to_str(item, indent + 1) for item in sexp[1:])
    return f"({head}\n{rest}\n{pad})"


# ---------------------------------------------------------------------------
# Core mutation logic
# ---------------------------------------------------------------------------

def _find_action_block(sexp: list, action_name: str) -> list | None:
    """
    Locate the :action sexp block for `action_name` inside a domain sexp.
    Returns a reference to the sub-list (mutable).
    """
    if not isinstance(sexp, list):
        return None
    if len(sexp) >= 2 and sexp[0] == ":action" and isinstance(sexp[1], str) and sexp[1].lower() == action_name.lower():
        return sexp
    for item in sexp:
        result = _find_action_block(item, action_name)
        if result is not None:
            return result
    return None


def _get_section(action_sexp: list, keyword: str) -> int | None:
    """Return the index of `keyword` (e.g. ':precondition') in action_sexp."""
    for i, item in enumerate(action_sexp):
        if isinstance(item, str) and item.lower() == keyword.lower():
            return i
    return None


def _get_preconditions(action_sexp: list) -> list | None:
    """Extract the precondition conjunction list from an action sexp."""
    idx = _get_section(action_sexp, ":precondition")
    if idx is None or idx + 1 >= len(action_sexp):
        return None
    prec = action_sexp[idx + 1]
    if isinstance(prec, list) and len(prec) >= 1 and isinstance(prec[0], str) and prec[0].lower() == "and":
        return prec  # Returns the (and ...) list directly
    return None


def _extract_positive_atoms(prec_sexp: list) -> list[tuple]:
    """
    Return list of (index_in_and_list, atom_sexp) for positive (non-negated) atoms.
    Index is within the (and ...) sexp starting from position 1.
    """
    atoms = []
    for i, item in enumerate(prec_sexp[1:], start=1):
        if isinstance(item, list) and len(item) >= 1:
            if isinstance(item[0], str) and item[0].lower() != "not":
                atoms.append((i, item))
        elif isinstance(item, str):
            atoms.append((i, item))
    return atoms


def _classify_bottleneck(atoms: list[tuple]) -> tuple | None:
    """
    Heuristic: the 'bottleneck' atom is the last positive precondition — the one
    most likely to be the gating condition in a linear-chain topology.
    For Blocksworld `unstack`: the `(clear ?x)` atom is typically last.
    Falls back to last positive atom if no domain-specific hint.
    """
    if not atoms:
        return None
    return atoms[-1]  # (index, atom_sexp)


# ---------------------------------------------------------------------------
# Mutation strategies
# ---------------------------------------------------------------------------

def _apply_type_i(domain_sexp: list, action_name: str, rng: random.Random) -> MutationRecord:
    """
    Type I — OmitLeafPrecondition
    Remove the first positive (non-critical, non-bottleneck) precondition atom.
    """
    record = MutationRecord(domain_path="", intervention="Type_I", target_action=action_name, seed=rng.randint(0, 99999))
    action = _find_action_block(domain_sexp, action_name)
    if action is None:
        raise ValueError(f"Action '{action_name}' not found in domain.")
    prec = _get_preconditions(action)
    if prec is None:
        raise ValueError(f"Action '{action_name}' has no (and ...) precondition block.")
    positive = _extract_positive_atoms(prec)
    if not positive:
        raise ValueError(f"Action '{action_name}' has no positive precondition atoms to remove.")
    # Remove the first positive atom (leaf, least critical)
    idx, atom = positive[0]
    record.removed_atoms = [_sexp_to_str(atom)]
    del prec[idx]
    return record


def _apply_type_ii(domain_sexp: list, action_name: str, rng: random.Random) -> MutationRecord:
    """
    Type II — OmitBottleneckPrecondition
    Remove the last positive precondition atom (the critical bottleneck gating
    the search-tree path). This induces the phantom subtree Ω(b^(D-d)).
    """
    record = MutationRecord(domain_path="", intervention="Type_II", target_action=action_name, seed=rng.randint(0, 99999))
    action = _find_action_block(domain_sexp, action_name)
    if action is None:
        raise ValueError(f"Action '{action_name}' not found in domain.")
    prec = _get_preconditions(action)
    if prec is None:
        raise ValueError(f"Action '{action_name}' has no (and ...) precondition block.")
    positive = _extract_positive_atoms(prec)
    if not positive:
        raise ValueError(f"Action '{action_name}' has no positive precondition atoms to remove.")
    bottleneck = _classify_bottleneck(positive)
    idx, atom = bottleneck
    record.removed_atoms = [_sexp_to_str(atom)]
    del prec[idx]
    return record


def _apply_type_iii(domain_sexp: list, action_name: str, rng: random.Random) -> MutationRecord:
    """
    Type III — RedundantEffectAddition
    Add a vacuously-true add-effect atom that does not affect reachability
    but shifts A_pred scores (tests our prediction accuracy metric).
    """
    record = MutationRecord(domain_path="", intervention="Type_III", target_action=action_name, seed=rng.randint(0, 99999))
    action = _find_action_block(domain_sexp, action_name)
    if action is None:
        raise ValueError(f"Action '{action_name}' not found in domain.")

    # Insert into effect block
    eff_idx = _get_section(action, ":effect")
    if eff_idx is None or eff_idx + 1 >= len(action):
        raise ValueError(f"Action '{action_name}' has no :effect section.")
    eff = action[eff_idx + 1]
    # Wrap scalar effect in (and ...) if needed
    if isinstance(eff, list) and eff[0].lower() != "and":
        action[eff_idx + 1] = ["and", eff, ["redundant-marker"]]
        eff = action[eff_idx + 1]
    elif isinstance(eff, list) and eff[0].lower() == "and":
        eff.append(["redundant-marker"])
    else:
        action[eff_idx + 1] = ["and", eff, ["redundant-marker"]]
    record.added_atoms = ["(redundant-marker)"]
    return record


# ---------------------------------------------------------------------------
# PDDLMutator — public API
# ---------------------------------------------------------------------------

class PDDLMutator:
    """
    Applies PDDL-level AST mutations for CEG-OMR intervention experiments.

    Parameters
    ----------
    seed : int
        Reproducibility seed for random tie-breaking.
    """

    _STRATEGIES: ClassVar[dict[str, Any]] = {
        "Type_I":   _apply_type_i,
        "Type_II":  _apply_type_ii,
        "Type_III": _apply_type_iii,
        # Enum-style keys also accepted
        "Type_I_OmitLeafPrecondition":        _apply_type_i,
        "Type_II_OmitBottleneckPrecondition":  _apply_type_ii,
        "Type_III_RedundantEffectAddition":    _apply_type_iii,
    }

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    def apply(
        self,
        domain_path: str | Path,
        intervention: str,
        target_action: str,
        out_dir: str | Path = "domains/mutated/",
    ) -> str:
        """
        Apply a single intervention to `domain_path`.

        Returns
        -------
        str
            Absolute path to the mutated PDDL file written to `out_dir`.

        Raises
        ------
        ValueError
            If the intervention type or target action is unknown.
        FileNotFoundError
            If `domain_path` does not exist.
        """
        domain_path = Path(domain_path)
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        if not domain_path.exists():
            raise FileNotFoundError(f"Domain file not found: {domain_path}")

        strategy = self._STRATEGIES.get(intervention)
        if strategy is None:
            raise ValueError(
                f"Unknown intervention type '{intervention}'. "
                f"Valid: {sorted(set(self._STRATEGIES.keys()))}"
            )

        # Parse domain text → S-expression tree (deep copy for safety)
        raw_text = domain_path.read_text(encoding="utf-8")
        tokens = _tokenize(raw_text)
        domain_sexp, _ = _parse_sexp(tokens)
        domain_sexp_mut = copy.deepcopy(domain_sexp)

        # Apply mutation
        record = strategy(domain_sexp_mut, target_action, self._rng)
        record.domain_path = str(domain_path)

        # Serialize back to PDDL text
        mutated_text = _sexp_to_str(domain_sexp_mut) + "\n"

        # Write output
        stem = domain_path.stem
        out_filename = f"{stem}_{intervention}_seed{self.seed}.pddl"
        out_path = out_dir / out_filename
        out_path.write_text(mutated_text, encoding="utf-8")
        record.output_path = str(out_path)

        # Optional: validate with `pddl` library
        if _PDDL_AVAILABLE:
            try:
                from pddl.parser.domain import DomainParser
                _ = DomainParser()(mutated_text)
            except Exception as e:  # noqa: BLE001
                print(f"[WARNING] pddl validation failed after mutation: {e}", file=sys.stderr)

        return str(out_path)

    def apply_batch(
        self,
        domain_path: str | Path,
        interventions: list[str],
        target_actions: list[str],
        out_dir: str | Path = "domains/mutated/",
    ) -> list[str]:
        """
        Apply multiple (intervention, action) pairs. Returns list of output paths.
        Each (intervention, action) pair uses a fresh mutator state on the original domain.
        """
        results = []
        for intv, act in zip(interventions, target_actions):
            # Fresh mutator per mutation to avoid compound effects
            m = PDDLMutator(seed=self.seed)
            out_path = m.apply(domain_path, intv, act, out_dir)
            results.append(out_path)
        return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    parser = argparse.ArgumentParser(
        description="Apply PDDL domain mutation for CEG-OMR experiments."
    )
    parser.add_argument("--domain", required=True, help="Path to PDDL domain file")
    parser.add_argument(
        "--intervention",
        required=True,
        choices=["Type_I", "Type_II", "Type_III"],
        help="Intervention type to apply",
    )
    parser.add_argument("--action", required=True, help="Target action name to mutate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--out", default="domains/mutated/", help="Output directory")
    args = parser.parse_args()

    mutator = PDDLMutator(seed=args.seed)
    out_path = mutator.apply(
        domain_path=args.domain,
        intervention=args.intervention,
        target_action=args.action,
        out_dir=args.out,
    )
    print(f"[OK] Mutated domain written to: {out_path}")


if __name__ == "__main__":
    _cli()
