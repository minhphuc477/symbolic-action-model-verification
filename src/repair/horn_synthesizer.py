"""
Horn Synthesizer & Version Space Candidate Elimination Component
================================================================
Implements bidirectional precondition and effect repair using pure version-space
candidate elimination, STRIPS Effect Coherence scoring, Iterative Deepening
Minimal Relaxation Search (ID-MRS), and offline planner-unsolvability backtracking.
"""

from __future__ import annotations

import copy
import itertools
import random
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pddl

from src.repair.config import Counterexample
from src.utils.sexp import (
    find_action_block,
    get_section,
    norm_sexp,
    parse_action_tuple,
    parse_sexp,
    sexp_to_str,
    tokenize,
)

if TYPE_CHECKING:
    from src.repair.generator import FastDownwardGenerator


def fastlas_succeeded(returncode: int, stderr: str) -> bool:
    """FastLAS contract: exits 0 always; check stderr for fatal errors."""
    return "Error" not in stderr and "error" not in stderr.lower()


def clingo_succeeded(returncode: int) -> bool:
    """Clingo contract: 10 = SAT, 30 = SAT (optimum found)."""
    return returncode in (10, 30)


class HornSynthesizer:
    """
    Synthesizer component: given a counterexample xi_t = <s_t, a_t, s_hat_{t+1}, s*_{t+1}>,
    updates candidate model M_hat using pure Active Version Space / Candidate Elimination (Mitchell 1982, Angluin 1992).

    CRITICAL SCIENTIFIC INTEGRITY:
    * ZERO access to ground truth domain file (M*).
    * Candidate hypotheses are generated strictly from M_hat's own predicate declarations and action parameters.
    * An applicability failure in state s_t implies that at least one necessary precondition evaluates to FALSE in s_t.
    * Candidates that evaluate to TRUE in s_t are eliminated from being the cause of failure.
    * Surviving candidates consistent with action effects (fluents deleted or modified by action) are prioritized.
    """

    def __init__(
        self,
        out_dir: str = "domains/mutated/",
        seed: int = 42,
        use_effect_coherence: bool = True,
        allow_effect_deletion: bool = True,
        max_relaxation_size: int = 3,
        max_suspects_per_level: int = 12,
    ):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self._rng = random.Random(seed)
        self.use_effect_coherence = use_effect_coherence
        self.allow_effect_deletion = allow_effect_deletion
        self.max_relaxation_size = max_relaxation_size
        self.max_suspects_per_level = max_suspects_per_level
        self.version_spaces: dict[str, set[str]] = {}
        self.refuted_candidates: dict[str, set[str]] = {}
        self.repair_history: list[dict[str, Any]] = []
        self.relaxed_candidates: dict[str, set[str]] = {}
        self.verified_necessary_preconditions: dict[str, set[str]] = {}
        self.tried_relaxations: set[tuple[tuple[str, str], ...]] = set()
        self.initial_preconditions: dict[str, set[str]] | None = None

    def _ensure_initial_preconditions(self, domain_path: str) -> None:
        if self.initial_preconditions is not None:
            return
        dom = pddl.parse_domain(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = tokenize(domain_text)
        domain_sexp, _ = parse_sexp(tokens)
        self.initial_preconditions = {}
        for pddl_act in dom.actions:
            act_name = pddl_act.name.lower()
            action_block = find_action_block(domain_sexp, act_name)
            if action_block is None:
                continue
            prec_idx = get_section(action_block, ":precondition")
            if prec_idx is None or prec_idx + 1 >= len(action_block):
                continue
            prec_sexp = action_block[prec_idx + 1]
            if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                conjuncts = prec_sexp[1:]
            elif isinstance(prec_sexp, list) and prec_sexp:
                conjuncts = [prec_sexp]
            else:
                conjuncts = []
            self.initial_preconditions[act_name] = {
                " ".join(sexp_to_str(c).split()).strip().lower() for c in conjuncts
            }

    def relax_overconstrained_domain(
        self,
        domain_path: str,
        problem_path: str,
        generator: FastDownwardGenerator,
        iteration: int,
        min_suspect_score: int = 0,
    ) -> tuple[bool, str, list[str], float]:
        """
        Minimal-Relaxation Abduction for over-constrained domains (where Pi(M_hat, s_0, g) is empty
        due to spurious preconditions or SAS+ sink-violation delete effects in M_hat_0).
        Ranks existing non-locked initial preconditions and delete effects by Inverse STRIPS
        Effect Coherence (suspect score) and finds a minimal removal that restores solvability
        in Fast Downward with zero oracle queries.
        """
        self._ensure_initial_preconditions(domain_path)
        dom = pddl.parse_domain(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = tokenize(domain_text)
        domain_sexp, _ = parse_sexp(tokens)

        # Collect predicate effect statistics across the domain
        dynamic_predicates: set[str] = set()
        ever_added_predicates: set[str] = set()
        conserved_predicates: set[str] = set()
        for pddl_act in dom.actions:
            eff_ops = (
                list(pddl_act.effect.operands)
                if hasattr(pddl_act.effect, "operands")
                else ([pddl_act.effect] if pddl_act.effect is not None else [])
            )
            act_add_preds: set[str] = set()
            act_del_preds: set[str] = set()
            for op in eff_ops:
                s = " ".join(str(op).split()).strip().lower()
                is_del = False
                if s.startswith("(not ") and s.endswith(")"):
                    s = s[5:-1].strip()
                    is_del = True
                toks = s.strip("()").split()
                if toks:
                    dynamic_predicates.add(toks[0])
                    if is_del:
                        act_del_preds.add(toks[0])
                    else:
                        ever_added_predicates.add(toks[0])
                        act_add_preds.add(toks[0])
            conserved_predicates |= (act_add_preds & act_del_preds)

        suspect_candidates: list[tuple[int, str, str, str]] = []  # (score, kind, act_name, norm_str)
        for pddl_act in dom.actions:
            act_name = pddl_act.name.lower()
            locked = self.verified_necessary_preconditions.get(act_name, set())
            init_precs = (
                self.initial_preconditions.get(act_name, set())
                if self.initial_preconditions is not None
                else None
            )

            deleted_literals: set[str] = set()
            added_literals: set[str] = set()
            eff_ops = (
                list(pddl_act.effect.operands)
                if hasattr(pddl_act.effect, "operands")
                else ([pddl_act.effect] if pddl_act.effect is not None else [])
            )
            for op in eff_ops:
                s = " ".join(str(op).split()).strip().lower()
                if s.startswith("(not ") and s.endswith(")"):
                    deleted_literals.add(s[5:-1].strip())
                else:
                    added_literals.add(s)

            action_block = find_action_block(domain_sexp, act_name)
            if action_block is None:
                continue
            prec_idx = get_section(action_block, ":precondition")
            if prec_idx is not None and prec_idx + 1 < len(action_block):
                prec_sexp = action_block[prec_idx + 1]
                if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                    conjuncts = prec_sexp[1:]
                elif isinstance(prec_sexp, list) and prec_sexp:
                    conjuncts = [prec_sexp]
                else:
                    conjuncts = []

                for c_sexp in conjuncts:
                    c_norm = norm_sexp(c_sexp)
                    if c_norm in locked:
                        continue
                    if init_precs is not None and c_norm not in init_precs:
                        continue
                    # Inverse STRIPS Effect Coherence suspect scoring
                    score = 5
                    if self.use_effect_coherence:
                        if c_norm in added_literals or c_norm.startswith("(not ") and c_norm.endswith(")") and c_norm[5:-1].strip() in deleted_literals:
                            score = 20
                        elif c_norm in deleted_literals:
                            score = 1
                        elif c_norm.startswith("(not ") and c_norm.endswith(")") and c_norm[5:-1].strip() in added_literals:
                            score = 2
                        else:
                            raw_pred = c_norm.strip("()").split()[0] if c_norm.strip("()") else ""
                            if raw_pred == "not":
                                inner_toks = c_norm[5:-1].strip().strip("()").split()
                                raw_pred = inner_toks[0] if inner_toks else ""
                            if raw_pred in dynamic_predicates:
                                score = 12
                            else:
                                score = 4
                    if score >= min_suspect_score:
                        suspect_candidates.append((score, "prec", act_name, c_norm))

            # Check for SAS+ Sink-Violation Spurious Delete Effects
            if self.allow_effect_deletion:
                act_add_preds_here = {
                    lit.strip("()").split()[0]
                    for lit in added_literals
                    if lit.strip("()").split()
                }
                for d_inner in sorted(deleted_literals):
                    toks = d_inner.strip("()").split()
                    if not toks:
                        continue
                    d_pred = toks[0]
                    del_norm = f"(not {d_inner})"
                    if del_norm in locked:
                        continue
                    if d_pred not in ever_added_predicates or (
                        d_pred in conserved_predicates and d_pred not in act_add_preds_here
                    ):
                        eff_score = 18
                        if eff_score >= min_suspect_score:
                            suspect_candidates.append((eff_score, "eff_del", act_name, del_norm))

        if not suspect_candidates:
            return False, domain_path, [], 0.0

        suspect_candidates.sort(key=lambda x: x[0], reverse=True)

        # Search minimal relaxations using Iterative Deepening Minimal Relaxation Search (ID-MRS)
        candidate_items = [(kind, act_name, c_norm) for _, kind, act_name, c_norm in suspect_candidates]
        relaxation_sets: list[tuple[tuple[str, str, str], ...]] = []
        for kappa in range(1, self.max_relaxation_size + 1):
            if kappa == 1:
                relaxation_sets.extend((item,) for item in candidate_items)
            else:
                top_k = candidate_items[: min(self.max_suspects_per_level, len(candidate_items))]
                relaxation_sets.extend(itertools.combinations(top_k, kappa))

        for relax_tuple in relaxation_sets:
            canon_key = tuple(sorted((f"{k}:{a}", c) for k, a, c in relax_tuple))
            if canon_key in self.tried_relaxations:
                continue

            domain_sexp_cand = copy.deepcopy(domain_sexp)
            modified = False
            for kind, act_name, target_norm in relax_tuple:
                action_block = find_action_block(domain_sexp_cand, act_name)
                if action_block is None:
                    continue
                if kind == "prec":
                    prec_idx = get_section(action_block, ":precondition")
                    if prec_idx is None or prec_idx + 1 >= len(action_block):
                        continue
                    prec_sexp = action_block[prec_idx + 1]
                    if isinstance(prec_sexp, list) and prec_sexp and isinstance(prec_sexp[0], str) and prec_sexp[0].lower() == "and":
                        new_conjuncts = [
                            c for c in prec_sexp[1:]
                            if norm_sexp(c) != target_norm
                        ]
                        if len(new_conjuncts) < len(prec_sexp) - 1:
                            action_block[prec_idx + 1] = ["and"] + new_conjuncts if new_conjuncts else ["and"]
                            modified = True
                    elif isinstance(prec_sexp, list) and norm_sexp(prec_sexp) == target_norm:
                        action_block[prec_idx + 1] = ["and"]
                        modified = True
                elif kind == "eff_del":
                    eff_idx = get_section(action_block, ":effect")
                    if eff_idx is None or eff_idx + 1 >= len(action_block):
                        continue
                    eff_sexp = action_block[eff_idx + 1]
                    if isinstance(eff_sexp, list) and eff_sexp and isinstance(eff_sexp[0], str) and eff_sexp[0].lower() == "and":
                        new_effs = [
                            c for c in eff_sexp[1:]
                            if norm_sexp(c) != target_norm
                        ]
                        if len(new_effs) < len(eff_sexp) - 1:
                            action_block[eff_idx + 1] = ["and"] + new_effs if new_effs else ["and"]
                            modified = True

            if not modified:
                continue

            cand_text = sexp_to_str(domain_sexp_cand) + "\n"
            cand_path = self.out_dir / f"relaxed_iter{iteration:03d}.pddl"
            cand_path.write_text(cand_text, encoding="utf-8")
            plan_file = str(self.out_dir / f"plan_relax_iter{iteration:03d}.soln")

            plan_found, plan, elapsed = generator.generate_plan(
                str(cand_path), problem_path, plan_file
            )
            if plan_found:
                self.tried_relaxations.add(canon_key)
                for kind, act_name, target_norm in relax_tuple:
                    self.relaxed_candidates.setdefault(act_name, set()).add(target_norm)
                    print(
                        f"[HornSynthesizer] Minimal-Relaxation Abduction removed suspect {kind} "
                        f"{target_norm} from {act_name}"
                    )
                return True, str(cand_path), plan, elapsed

        return False, domain_path, [], 0.0

    def rollback(self, iteration: int) -> tuple[bool, str]:
        """
        Backtrack if planner failed: pop the last added hypothesis,
        mark it as refuted, and try the next surviving candidate if available.
        """
        while self.repair_history:
            last = self.repair_history.pop()
            act_name = last["action"]
            chosen = last["chosen"]
            prev_domain_path = last["domain_before_path"]
            remaining = last["remaining"]

            self.refuted_candidates.setdefault(act_name, set()).add(chosen)
            if act_name in self.version_spaces:
                self.version_spaces[act_name].discard(chosen)

            print(f"[HornSynthesizer] Backtracking: refuted over-constraining hypothesis {chosen} on {act_name}")

            while remaining:
                next_cand = remaining.pop(0)
                if next_cand in self.refuted_candidates.get(act_name, set()):
                    continue

                domain_text = Path(prev_domain_path).read_text(encoding="utf-8")
                tokens = tokenize(domain_text)
                domain_sexp, _ = parse_sexp(tokens)
                domain_sexp_rep = copy.deepcopy(domain_sexp)
                action = find_action_block(domain_sexp_rep, act_name)
                if action is not None:
                    prec_idx = get_section(action, ":precondition")
                    if prec_idx is not None and prec_idx + 1 < len(action):
                        prec = action[prec_idx + 1]
                        cand_tokens = tokenize(next_cand)
                        cand_sexp, _ = parse_sexp(cand_tokens) if cand_tokens else (None, 0)
                        if cand_sexp is not None:
                            if isinstance(prec, list) and prec and prec[0].lower() == "and":
                                prec.append(cand_sexp)
                            else:
                                action[prec_idx + 1] = ["and", prec, cand_sexp]

                repaired_text = sexp_to_str(domain_sexp_rep) + "\n"
                out_name = f"repaired_backtrack_iter{iteration:03d}.pddl"
                out_path = self.out_dir / out_name
                out_path.write_text(repaired_text, encoding="utf-8")

                self.repair_history.append({
                    "action": act_name,
                    "chosen": next_cand,
                    "domain_before_path": prev_domain_path,
                    "remaining": remaining,
                    "iteration": iteration,
                    "chosen_score": last.get("chosen_score", 0),
                })
                print(f"[HornSynthesizer] Retrying with alternative candidate: {next_cand}")
                return True, str(out_path)

            return True, prev_domain_path

        return False, ""

    def repair(
        self,
        domain_path: str,
        counterexample: Counterexample,
        iteration: int,
    ) -> str:
        """
        Repair M_hat by eliminating phantom preconditions or repairing 4-way effect deltas
        using active counterexample feedback.
        """
        self._ensure_initial_preconditions(domain_path)
        domain_text = Path(domain_path).read_text(encoding="utf-8")
        tokens = tokenize(domain_text)
        domain_sexp, _ = parse_sexp(tokens)
        domain_sexp_rep = copy.deepcopy(domain_sexp)

        act_name, args = parse_action_tuple(counterexample.action)

        dom = pddl.parse_domain(domain_path)
        matching_actions = [a for a in dom.actions if a.name.lower() == act_name.lower()]
        if not matching_actions:
            return domain_path
        pddl_act = matching_actions[0]

        action = find_action_block(domain_sexp_rep, act_name)
        if action is None:
            return domain_path

        existing_preconditions: set[str] = set()
        if hasattr(pddl_act.precondition, "operands"):
            for op in pddl_act.precondition.operands:
                existing_preconditions.add(" ".join(str(op).split()).strip().lower())
        elif pddl_act.precondition is not None:
            existing_preconditions.add(" ".join(str(pddl_act.precondition).split()).strip().lower())

        deleted_literals: set[str] = set()
        added_literals: set[str] = set()
        if hasattr(pddl_act.effect, "operands"):
            for op in pddl_act.effect.operands:
                s = " ".join(str(op).split()).strip().lower()
                if s.startswith("(not ") and s.endswith(")"):
                    deleted_literals.add(s[5:-1].strip())
                else:
                    added_literals.add(s)
        elif pddl_act.effect is not None:
            s = " ".join(str(pddl_act.effect).split()).strip().lower()
            if s.startswith("(not ") and s.endswith(")"):
                deleted_literals.add(s[5:-1].strip())
            else:
                added_literals.add(s)

        failure_state_literals = {
            tok.strip().lower()
            for tok in re.findall(r"\([^()]+\)", counterexample.current_state)
        }

        act_params = list(pddl_act.parameters)
        pmap = {p.name.lower(): arg_val.lower() for p, arg_val in zip(act_params, args)}
        inv_pmap = {arg_val.lower(): "?" + p.name.lstrip("?").lower() for p, arg_val in zip(act_params, args)}

        # TYPE III/IV BIDIRECTIONAL EFFECT REPAIR
        if counterexample.failure_type == "wrong_effect":
            pred_lits = {tok.strip().lower() for tok in re.findall(r"\([^()]+\)", counterexample.predicted_next)}
            actual_lits = {tok.strip().lower() for tok in re.findall(r"\([^()]+\)", counterexample.actual_next)}
            actual_minus_pred = actual_lits - pred_lits
            pred_minus_actual = pred_lits - actual_lits

            eff_idx = get_section(action, ":effect")
            if eff_idx is not None and eff_idx + 1 < len(action):
                eff = action[eff_idx + 1]

                def _variablize_atom(atom_str: str) -> str | None:
                    inner = atom_str.strip("()")
                    parts = inner.split()
                    if not parts:
                        return None
                    pname = parts[0]
                    vargs = []
                    for arg in parts[1:]:
                        if arg.lower() in inv_pmap:
                            vargs.append(inv_pmap[arg.lower()])
                        else:
                            return None
                    return f"({pname} {' '.join(vargs)})"

                def _has_matching_del(eff_block: list, target_pos_norm: str) -> bool:
                    target_norm = " ".join(f"(not {target_pos_norm})".split()).strip().lower()
                    return any(" ".join(sexp_to_str(x).split()).strip().lower() == target_norm for x in eff_block[1:])

                def _remove_matching_del(eff_block: list, target_pos_norm: str) -> None:
                    target_norm = " ".join(f"(not {target_pos_norm})".split()).strip().lower()
                    eff_block[1:] = [x for x in eff_block[1:] if " ".join(sexp_to_str(x).split()).strip().lower() != target_norm]

                for missing_lit in actual_minus_pred:
                    var_schema = _variablize_atom(missing_lit)
                    if var_schema:
                        var_norm = " ".join(var_schema.split()).strip().lower()
                        if _has_matching_del(eff, var_norm):
                            _remove_matching_del(eff, var_norm)
                            print(f"[HornSynthesizer] Repaired spurious delete effect on {act_name}: removed (not {var_schema})")
                        else:
                            cand_tokens = tokenize(var_schema)
                            cand_sexp, _ = parse_sexp(cand_tokens) if cand_tokens else (None, 0)
                            if cand_sexp is not None:
                                eff.append(cand_sexp)
                                print(f"[HornSynthesizer] Repaired missing add effect on {act_name}: added {var_schema}")

                for spurious_lit in pred_minus_actual:
                    var_schema = _variablize_atom(spurious_lit)
                    if var_schema:
                        var_norm = " ".join(var_schema.split()).strip().lower()
                        existing_effs = [" ".join(sexp_to_str(x).split()).strip().lower() for x in eff[1:]]
                        if var_norm in existing_effs:
                            eff[1:] = [x for x in eff[1:] if " ".join(sexp_to_str(x).split()).strip().lower() != var_norm]
                            print(f"[HornSynthesizer] Repaired spurious add effect on {act_name}: removed {var_schema}")
                        else:
                            del_schema = f"(not {var_schema})"
                            del_tokens = tokenize(del_schema)
                            del_sexp, _ = parse_sexp(del_tokens) if del_tokens else (None, 0)
                            if del_sexp is not None:
                                eff.append(del_sexp)
                                print(f"[HornSynthesizer] Repaired missing delete effect on {act_name}: added {del_schema}")

            repaired_text = sexp_to_str(domain_sexp_rep) + "\n"
            out_name = f"repaired_iter{iteration:03d}.pddl"
            out_path = self.out_dir / out_name
            out_path.write_text(repaired_text, encoding="utf-8")
            return str(out_path)

        # PRECONDITION REPAIR
        dom_types: dict[str, str] = {}
        if hasattr(dom, "types"):
            for t_name, t_parent in dom.types.items():
                dom_types[str(t_name).lower()] = str(t_parent).lower() if t_parent else ""

        def _is_type_compatible(param_types: set[str], term_types: set[str]) -> bool:
            if not term_types or not param_types:
                return True
            p_type_tags = {str(t).lower() for t in param_types}
            t_type_tags = {str(t).lower() for t in term_types}
            if p_type_tags & t_type_tags:
                return True
            for pt in p_type_tags:
                curr = pt
                while curr:
                    if curr in t_type_tags:
                        return True
                    curr = dom_types.get(curr, "")
            return False

        candidate_atoms: list[tuple[str, str, bool]] = []
        for pred in dom.predicates:
            pred_terms = list(pred.terms)
            arity = len(pred_terms)
            if arity == 0:
                pos_schema = f"({pred.name})"
                if pos_schema.lower() not in existing_preconditions and pos_schema.lower() not in added_literals:
                    candidate_atoms.append((pos_schema, pos_schema.lower(), False))
                neg_schema = f"(not ({pred.name}))"
                if (
                    neg_schema.lower() not in existing_preconditions
                    and pos_schema.lower() not in existing_preconditions
                    and pos_schema.lower() not in deleted_literals
                ):
                    candidate_atoms.append((neg_schema, pos_schema.lower(), True))
            else:
                matching_param_lists = []
                for t in pred_terms:
                    t_types = set(t.type_tags) if t.type_tags else set()
                    matches = []
                    for p in act_params:
                        p_types = set(p.type_tags) if p.type_tags else set()
                        if _is_type_compatible(p_types, t_types):
                            matches.append(p.name)
                    matching_param_lists.append(matches)

                for p_tuple in itertools.product(*matching_param_lists):
                    if len(p_tuple) > 1 and len(set(p_tuple)) < len(p_tuple):
                        continue
                    grounded = [pmap.get(pt.lower(), pt.lower()) for pt in p_tuple]
                    atom_grounded = f"({pred.name} {' '.join(grounded)})".lower()

                    pos_schema = f"({pred.name} {' '.join('?' + p.lstrip('?') for p in p_tuple)})"
                    if pos_schema.lower() not in existing_preconditions and pos_schema.lower() not in added_literals:
                        candidate_atoms.append((pos_schema, atom_grounded, False))

                    neg_schema = f"(not ({pred.name} {' '.join('?' + p.lstrip('?') for p in p_tuple)}))"
                    if (
                        neg_schema.lower() not in existing_preconditions
                        and pos_schema.lower() not in existing_preconditions
                        and pos_schema.lower() not in deleted_literals
                    ):
                        candidate_atoms.append((neg_schema, atom_grounded, True))

        refuted = self.refuted_candidates.get(act_name, set())
        violating_candidates: list[str] = []

        for schema_str, grounded_str, is_neg in candidate_atoms:
            if schema_str in refuted:
                continue
            if not is_neg:
                if grounded_str not in failure_state_literals:
                    violating_candidates.append(schema_str)
            else:
                if grounded_str in failure_state_literals:
                    violating_candidates.append(schema_str)

        if not violating_candidates:
            return domain_path

        def candidate_score(c_str: str) -> int:
            clean = c_str.strip().lower()
            sc = 0
            is_neg = clean.startswith("(not ") and clean.endswith(")")
            raw_atom = clean[5:-1].strip() if is_neg else clean
            raw_pred = raw_atom.strip("()").split()[0] if raw_atom.strip("()") else ""

            if not is_neg:
                if clean in deleted_literals:
                    sc += 10
                elif any(lit.strip("()").split()[0] == raw_pred for lit in deleted_literals if lit.strip("()").split()):
                    sc += 6
                if clean in added_literals:
                    sc -= 20
                clean_norm = " ".join(clean.split()).strip().lower()
                if clean_norm in self.relaxed_candidates.get(act_name, set()):
                    sc += 15
            else:
                if raw_atom in added_literals:
                    sc += 10
                elif any(lit.strip("()").split()[0] == raw_pred for lit in added_literals if lit.strip("()").split()):
                    sc += 6
                if raw_atom in deleted_literals:
                    sc -= 20
                clean_norm = " ".join(clean.split()).strip().lower()
                if clean_norm in self.relaxed_candidates.get(act_name, set()):
                    sc += 15
            return sc

        if self.use_effect_coherence:
            violating_candidates.sort(key=candidate_score, reverse=True)
            chosen_candidate = violating_candidates[0]
            remaining_candidates = violating_candidates[1:]
        else:
            chosen_candidate = self._rng.choice(violating_candidates)
            remaining_candidates = [c for c in violating_candidates if c != chosen_candidate]

        prec_idx = get_section(action, ":precondition")
        if prec_idx is not None and prec_idx + 1 < len(action):
            prec = action[prec_idx + 1]
            cand_tokens = tokenize(chosen_candidate)
            cand_sexp, _ = parse_sexp(cand_tokens) if cand_tokens else (None, 0)
            if cand_sexp is not None:
                if isinstance(prec, list) and prec and prec[0].lower() == "and":
                    prec.append(cand_sexp)
                else:
                    action[prec_idx + 1] = ["and", prec, cand_sexp]
                print(f"[HornSynthesizer] Refined action {act_name} with: {chosen_candidate}")

        chosen_norm = " ".join(chosen_candidate.split()).strip().lower()
        if chosen_norm in self.relaxed_candidates.get(act_name, set()):
            self.verified_necessary_preconditions.setdefault(act_name, set()).add(chosen_norm)
            print(f"[HornSynthesizer] Locked verified necessary precondition {chosen_norm} on {act_name}")
        else:
            self.repair_history.append({
                "action": act_name,
                "chosen": chosen_candidate,
                "domain_before_path": domain_path,
                "remaining": remaining_candidates,
                "iteration": iteration,
                "chosen_score": candidate_score(chosen_candidate) if self.use_effect_coherence else 0,
            })

        repaired_text = sexp_to_str(domain_sexp_rep) + "\n"
        out_name = f"repaired_iter{iteration:03d}.pddl"
        out_path = self.out_dir / out_name
        out_path.write_text(repaired_text, encoding="utf-8")
        return str(out_path)


# Backward compatibility aliases
_fastlas_succeeded = fastlas_succeeded
_clingo_succeeded = clingo_succeeded
