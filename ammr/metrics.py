"""AMLGym-compatible syntactic, predictive, and held-out solving evaluation metrics."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass

from ammr.pddl.model import Action, Atom, Domain, GroundAction, Problem, State, ground_actions
from ammr.planner import Planner, PlanStatus, validate_plan


@dataclass(frozen=True)
class SyntacticReport:
    precision: float
    recall: float
    f1: float
    pre_pos_f1: float
    pre_neg_f1: float
    add_f1: float
    del_f1: float
    edit_distance: int


@dataclass(frozen=True)
class PredictiveReport:
    applicability_precision: float
    applicability_recall: float
    effects_precision: float
    effects_recall: float
    transition_accuracy: float
    fluent_accuracy: float


@dataclass(frozen=True)
class SolvingReport:
    solving_ratio: float
    false_plans_ratio: float
    unsolvable_ratio: float
    timeout_ratio: float


def _prf(pred: frozenset[Atom], gt: frozenset[Atom]) -> tuple[float, float, float]:
    if not pred and not gt:
        return 1.0, 1.0, 1.0
    tp = len(pred & gt)
    fp = len(pred - gt)
    fn = len(gt - pred)
    p = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2.0 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return p, r, f1


def syntactic_metrics(evaluated: Domain, reference: Domain) -> SyntacticReport:
    """Compute AMLGym operator-averaged syntactic precision/recall/F1 and edit distance."""
    p_all: list[float] = []
    r_all: list[float] = []
    f_all: list[float] = []
    f_pp: list[float] = []
    f_pn: list[float] = []
    f_add: list[float] = []
    f_del: list[float] = []
    edits = 0

    for name, ref_op in reference.actions.items():
        ev_op = evaluated.actions.get(name, Action(name, ref_op.params))
        _, _, f1_pp = _prf(ev_op.pre_pos, ref_op.pre_pos)
        _, _, f1_pn = _prf(ev_op.pre_neg, ref_op.pre_neg)
        _, _, f1_a = _prf(ev_op.add, ref_op.add)
        _, _, f1_d = _prf(ev_op.delete, ref_op.delete)
        f_pp.append(f1_pp)
        f_pn.append(f1_pn)
        f_add.append(f1_a)
        f_del.append(f1_d)

        tp = (
            len(ev_op.pre_pos & ref_op.pre_pos)
            + len(ev_op.pre_neg & ref_op.pre_neg)
            + len(ev_op.add & ref_op.add)
            + len(ev_op.delete & ref_op.delete)
        )
        fp = (
            len(ev_op.pre_pos - ref_op.pre_pos)
            + len(ev_op.pre_neg - ref_op.pre_neg)
            + len(ev_op.add - ref_op.add)
            + len(ev_op.delete - ref_op.delete)
        )
        fn = (
            len(ref_op.pre_pos - ev_op.pre_pos)
            + len(ref_op.pre_neg - ev_op.pre_neg)
            + len(ref_op.add - ev_op.add)
            + len(ref_op.delete - ev_op.delete)
        )
        edits += fp + fn
        p = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (
            (2.0 * p * r / (p + r))
            if (p + r) > 0
            else (1.0 if tp == 0 and fp == 0 and fn == 0 else 0.0)
        )
        p_all.append(p)
        r_all.append(r)
        f_all.append(f1)

    n = max(1, len(reference.actions))
    return SyntacticReport(
        precision=sum(p_all) / n,
        recall=sum(r_all) / n,
        f1=sum(f_all) / n,
        pre_pos_f1=sum(f_pp) / n,
        pre_neg_f1=sum(f_pn) / n,
        add_f1=sum(f_add) / n,
        del_f1=sum(f_del) / n,
        edit_distance=edits,
    )


def sample_reachable_states(
    reference: Domain, problems: Sequence[Problem], max_states: int = 30, seed: int = 0
) -> list[tuple[Problem, State]]:
    """Collect reachable ground states from ``reference`` via seeded random walks."""
    rng = random.Random(seed)
    collected: list[tuple[Problem, State]] = []
    per_prob = max(1, max_states // max(1, len(problems)))
    for prob in problems:
        ops = list(ground_actions(reference, prob))
        state = prob.init
        collected.append((prob, state))
        for _ in range(per_prob * 3):
            if len(collected) >= max_states:
                break
            app = [ga for ga in ops if reference.actions[ga[0]].is_applicable(state, ga[1])]
            if not app:
                break
            act_name, args = rng.choice(app)
            state = reference.actions[act_name].successor(state, args)
            collected.append((prob, state))
    return collected[:max_states]


def predictive_metrics(
    evaluated: Domain,
    reference: Domain,
    problem_states: Sequence[tuple[Problem, State]],
    universe_cache: dict[str, int] | None = None,
) -> PredictiveReport:
    """Compute AMLGym applicability/effects P/R and one-step transition & fluent accuracy."""
    app_tp = {op: 0 for op in reference.actions}
    app_fp = {op: 0 for op in reference.actions}
    app_fn = {op: 0 for op in reference.actions}
    eff_tp = {op: 0 for op in reference.actions}
    eff_fp = {op: 0 for op in reference.actions}
    eff_fn = {op: 0 for op in reference.actions}

    ops_by_prob: dict[str, list[GroundAction]] = {}
    total_pairs = 0
    exact_transitions = 0
    total_fluent_checks = 0
    exact_fluent_checks = 0

    for prob, s in problem_states:
        if prob.name not in ops_by_prob:
            ops_by_prob[prob.name] = list(ground_actions(reference, prob))
        u_size = (universe_cache or {}).get(prob.name, max(1, len(s) * 2))
        for op_name, args in ops_by_prob[prob.name]:
            ref_act = reference.actions[op_name]
            ev_act = evaluated.actions[op_name]
            r_app = ref_act.is_applicable(s, args)
            e_app = ev_act.is_applicable(s, args)
            total_pairs += 1
            if r_app and e_app:
                app_tp[op_name] += 1
                s_ref = ref_act.successor(s, args)
                s_ev = ev_act.successor(s, args)
                if s_ref == s_ev:
                    exact_transitions += 1
                diff = len(s_ref ^ s_ev)
                total_fluent_checks += u_size
                exact_fluent_checks += max(0, u_size - diff)

                add_r, del_r = s_ref - s, s - s_ref
                add_e, del_e = s_ev - s, s - s_ev
                eff_tp[op_name] += len(add_e & add_r) + len(del_e & del_r)
                eff_fp[op_name] += len(add_e - add_r) + len(del_e - del_r)
                eff_fn[op_name] += len(add_r - add_e) + len(del_r - del_e)
            elif not r_app and not e_app:
                exact_transitions += 1
            elif e_app and not r_app:
                app_fp[op_name] += 1
            else:
                app_fn[op_name] += 1

    n_ops = max(1, len(reference.actions))
    ap = (
        sum(
            (app_tp[o] / (app_tp[o] + app_fp[o]) if (app_tp[o] + app_fp[o]) > 0 else 1.0)
            for o in reference.actions
        )
        / n_ops
    )
    ar = (
        sum(
            (app_tp[o] / (app_tp[o] + app_fn[o]) if (app_tp[o] + app_fn[o]) > 0 else 1.0)
            for o in reference.actions
        )
        / n_ops
    )
    ep = (
        sum(
            (eff_tp[o] / (eff_tp[o] + eff_fp[o]) if (eff_tp[o] + eff_fp[o]) > 0 else 1.0)
            for o in reference.actions
        )
        / n_ops
    )
    er = (
        sum(
            (eff_tp[o] / (eff_tp[o] + eff_fn[o]) if (eff_tp[o] + eff_fn[o]) > 0 else 1.0)
            for o in reference.actions
        )
        / n_ops
    )

    return PredictiveReport(
        applicability_precision=ap,
        applicability_recall=ar,
        effects_precision=ep,
        effects_recall=er,
        transition_accuracy=exact_transitions / max(1, total_pairs),
        fluent_accuracy=exact_fluent_checks / max(1, total_fluent_checks),
    )


def solving_metrics(
    evaluated: Domain,
    reference: Domain,
    problems: Sequence[Problem],
    planner: Planner,
    timeout_s: float = 15.0,
) -> SolvingReport:
    """Compute AMLGym solving_ratio, false_plans_ratio, unsolvable_ratio, and timeout_ratio."""
    if not problems:
        return SolvingReport(0.0, 0.0, 0.0, 0.0)
    solved = false_p = unsolv = tout = 0
    for prob in problems:
        res = planner.solve(evaluated, prob, timeout_s=timeout_s)
        if res.status == PlanStatus.SOLVED:
            if validate_plan(reference, prob, res.plan):
                solved += 1
            else:
                false_p += 1
        elif res.status == PlanStatus.UNSOLVABLE:
            unsolv += 1
        else:
            tout += 1
    n = len(problems)
    return SolvingReport(
        solving_ratio=solved / n,
        false_plans_ratio=false_p / n,
        unsolvable_ratio=unsolv / n,
        timeout_ratio=tout / n,
    )
