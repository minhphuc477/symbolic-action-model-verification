"""Closed-loop online action-model repair with planner-side relaxation."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ammr.env import Environment, ObservationMode, PartialState, StepOutcome
from ammr.faults import AtomicEdit, apply_edit, dynamic_predicates
from ammr.pddl.io import write_domain
from ammr.pddl.model import (
    EQ,
    Atom,
    Domain,
    GroundAction,
    Problem,
    State,
    ground_actions,
    ground_atom,
    ground_universe,
)
from ammr.planner import Planner, PlanResult, PlanStatus
from ammr.repair.hypotheses import DomainVersionSpace
from ammr.repair.update import TieBreak, project_action_candidates, project_domain


@dataclass(frozen=True)
class RepairResult:
    """Summary of an online repair run across one or more training problems."""

    repaired_domain: Domain
    solved_training: tuple[bool, ...]
    steps_used: int
    episodes: int
    planner_calls: int
    relaxation_accepts: int
    trace: tuple[StepOutcome, ...]


def is_relaxed_reachable(
    domain: Domain,
    problem: Problem,
    ground_ops: Sequence[GroundAction],
    universe: frozenset[Atom],
) -> bool:
    """Sound two-valued delete-relaxation reachability check (zero false negatives)."""
    f_pos: set[Atom] = set(problem.init)
    f_neg: set[Atom] = set(universe - problem.init)
    if problem.goal_pos <= f_pos and problem.goal_neg <= f_neg:
        return True

    pending = list(ground_ops)
    while pending:
        nxt_pending: list[GroundAction] = []
        progressed = False
        for act_name, args in pending:
            act = domain.actions[act_name]
            b = act.bind(args)
            ok = True
            for atom in act.pre_pos:
                if atom[0] == EQ:
                    ok = b.get(atom[1], atom[1]) == b.get(atom[2], atom[2])
                else:
                    ok = ground_atom(atom, b) in f_pos
                if not ok:
                    break
            if ok:
                for atom in act.pre_neg:
                    if atom[0] == EQ:
                        ok = b.get(atom[1], atom[1]) != b.get(atom[2], atom[2])
                    else:
                        ok = ground_atom(atom, b) in f_neg
                    if not ok:
                        break
            if not ok:
                nxt_pending.append((act_name, args))
                continue
            for atom in act.add:
                g = ground_atom(atom, b)
                if g not in f_pos:
                    f_pos.add(g)
                    progressed = True
            for atom in act.delete:
                g = ground_atom(atom, b)
                if g not in f_neg:
                    f_neg.add(g)
                    progressed = True
        if problem.goal_pos <= f_pos and problem.goal_neg <= f_neg:
            return True
        if not progressed:
            return False
        pending = nxt_pending
    return problem.goal_pos <= f_pos and problem.goal_neg <= f_neg


def _relaxation_edits(
    domain: Domain, vspace: DomainVersionSpace, goal_preds: set[str]
) -> list[AtomicEdit]:
    """Enumerate 1-edit reachability relaxations ordered by structural relevance."""
    dyn = dynamic_predicates(domain)
    pre_preds = {
        a[0] for act in domain.actions.values() for a in (*act.pre_pos, *act.pre_neg)
    } | goal_preds
    high: list[AtomicEdit] = []
    low: list[AtomicEdit] = []
    for name in sorted(domain.actions):
        act = domain.actions[name]
        hyp = vspace.actions[name]
        for atom in sorted(act.pre_pos):
            if atom[0] != EQ:
                high.append(AtomicEdit(name, "rem_pre_pos", atom))
        for atom in sorted(act.pre_neg):
            if atom[0] != EQ:
                high.append(AtomicEdit(name, "rem_pre_neg", atom))
        for atom in sorted(act.delete - hyp.forced_del):
            high.append(AtomicEdit(name, "rem_del", atom))
        for atom in hyp.candidates:
            if atom in act.add or atom in hyp.forbidden_add:
                continue
            edit = AtomicEdit(name, "add_add", atom)
            if atom[0] in pre_preds or atom[0] in dyn:
                high.append(edit)
            else:
                low.append(edit)
    return high + low


class OnlineDomainRepair:
    """Closed-loop agent combining version-space diagnosis and planner relaxation."""

    def __init__(
        self,
        tie_break: TieBreak = "lex",
        planner_timeout_s: float = 10.0,
        max_relax_checks: int = 50,
    ) -> None:
        self.tie_break: TieBreak = tie_break
        self.planner_timeout_s = planner_timeout_s
        self.max_relax_checks = max_relax_checks

    def _search_solvable_variant(
        self,
        active_prior: Domain,
        cur_domain: Domain,
        problem: Problem,
        vspace: DomainVersionSpace,
        planner: Planner,
        ops: Sequence[GroundAction],
        univ: frozenset[Atom],
    ) -> tuple[Domain, Domain, PlanResult, int, bool] | None:
        """Find a consistent hitting-set variant or minimal relaxation solving ``problem``."""
        calls = 0
        dyn = dynamic_predicates(active_prior)

        # 1. Check alternative minimum-cardinality hitting sets (0 prior relaxations)
        for name in sorted(active_prior.actions):
            variants = project_action_candidates(
                active_prior.actions[name], vspace.actions[name], dyn, self.tie_break
            )
            for alt_act in variants[1:]:
                cand = cur_domain.with_action(alt_act)
                sig = write_domain(cand)
                if sig in vspace.refuted_domains or not vspace.is_domain_consistent(cand):
                    continue
                if not is_relaxed_reachable(cand, problem, ops, univ):
                    vspace.refuted_domains.add(sig)
                    continue
                calls += 1
                res = planner.solve(cand, problem, self.planner_timeout_s)
                if res.status == PlanStatus.SOLVED:
                    return active_prior, cand, res, calls, False
                if res.status == PlanStatus.UNSOLVABLE:
                    vspace.refuted_domains.add(sig)

        # 2. Check 1-edit relaxations of cur_domain consistent with vspace
        goal_preds = {a[0] for a in (*problem.goal_pos, *problem.goal_neg)}
        edits1 = _relaxation_edits(cur_domain, vspace, goal_preds)
        valid_single: list[tuple[AtomicEdit, Domain]] = []
        for edit in edits1:
            if calls >= self.max_relax_checks:
                break
            cand = apply_edit(cur_domain, edit)
            if not vspace.is_domain_consistent(cand):
                continue
            valid_single.append((edit, cand))
            sig = write_domain(cand)
            if sig in vspace.refuted_domains:
                continue
            if not is_relaxed_reachable(cand, problem, ops, univ):
                vspace.refuted_domains.add(sig)
                continue
            calls += 1
            res = planner.solve(cand, problem, self.planner_timeout_s)
            if res.status == PlanStatus.SOLVED:
                return apply_edit(active_prior, edit), cand, res, calls, True
            if res.status == PlanStatus.UNSOLVABLE:
                vspace.refuted_domains.add(sig)

        # 3. Check 2-edit relaxations when 1-edit is still relaxed-unreachable / unsolvable
        short_pool = [e for e, _ in valid_single if e.kind != "add_add" or e.atom[0] in goal_preds][
            :30
        ]
        for idx, e1 in enumerate(short_pool):
            for e2 in short_pool[idx + 1 :]:
                if calls >= self.max_relax_checks:
                    return None
                if e1.action == e2.action and e1.atom == e2.atom:
                    continue
                cand = apply_edit(apply_edit(cur_domain, e1), e2)
                sig = write_domain(cand)
                if sig in vspace.refuted_domains or not vspace.is_domain_consistent(cand):
                    continue
                if not is_relaxed_reachable(cand, problem, ops, univ):
                    vspace.refuted_domains.add(sig)
                    continue
                calls += 1
                res = planner.solve(cand, problem, self.planner_timeout_s)
                if res.status == PlanStatus.SOLVED:
                    nxt_prior = apply_edit(apply_edit(active_prior, e1), e2)
                    return nxt_prior, cand, res, calls, True
                if res.status == PlanStatus.UNSOLVABLE:
                    vspace.refuted_domains.add(sig)
        return None

    def run(
        self,
        prior_domain: Domain,
        problems: Sequence[Problem],
        env_factory: Callable[[Problem, int], Environment],
        planner: Planner,
        total_step_budget: int = 200,
    ) -> RepairResult:
        vspace = DomainVersionSpace(prior_domain)
        confirmed_prior = prior_domain
        steps_used = 0
        episodes = 0
        planner_calls = 0
        relax_accepts = 0
        trace: list[StepOutcome] = []
        solved_flags: list[bool] = []

        for prob in problems:
            rem = total_step_budget - steps_used
            if rem <= 0:
                solved_flags.append(False)
                continue
            env = env_factory(prob, rem)
            ops = list(ground_actions(prior_domain, prob))
            univ = ground_universe(prior_domain, prob)
            prefix_cache: dict[tuple[GroundAction, ...], PartialState] = {}
            prob_solved = False
            unchanged_streak = 0
            prev_sig = ""

            while env.remaining_steps > 0 and not prob_solved:
                tentative_prior = confirmed_prior
                cur_domain = project_domain(confirmed_prior, vspace, self.tie_break)
                sig = write_domain(cur_domain)
                if sig in vspace.refuted_domains:
                    plan_res = PlanResult(PlanStatus.UNSOLVABLE)
                else:
                    planner_calls += 1
                    plan_res = planner.solve(cur_domain, prob, self.planner_timeout_s)

                used_relax = False
                if plan_res.status == PlanStatus.UNSOLVABLE:
                    vspace.refuted_domains.add(sig)
                    found = self._search_solvable_variant(
                        confirmed_prior, cur_domain, prob, vspace, planner, ops, univ
                    )
                    if found is None:
                        break
                    tentative_prior, cur_domain, plan_res, extra_calls, used_relax = found
                    sig = write_domain(cur_domain)
                    planner_calls += extra_calls
                elif plan_res.status != PlanStatus.SOLVED:
                    break

                env.reset()
                episodes += 1
                if prob.goal_reached(prob.init):
                    prob_solved = True
                    if used_relax:
                        confirmed_prior = tentative_prior
                        relax_accepts += 1
                    break

                pred_state: State = prob.init
                prefix: list[GroundAction] = []
                budget_hit = False

                for ga in plan_res.plan:
                    if env.remaining_steps == 0:
                        budget_hit = True
                        break
                    outcome = env.step(ga)
                    trace.append(outcome)
                    prefix_key = tuple(prefix)

                    if env.mode == ObservationMode.BINARY:
                        fb = PartialState(pos=pred_state, neg=univ - pred_state)
                        vspace.observe_step(outcome, fallback_before=fb, provisional=bool(prefix))
                    elif env.mode == ObservationMode.PARTIAL:
                        prev = prefix_cache.get(prefix_key, PartialState())
                        merged_before = PartialState(
                            pos=prev.pos | outcome.obs_before.pos,
                            neg=prev.neg | outcome.obs_before.neg,
                        )
                        prefix_cache[prefix_key] = merged_before
                        nxt_key = (*prefix_key, ga) if outcome.applicable else prefix_key
                        prev_after = prefix_cache.get(nxt_key, PartialState())
                        merged_after = PartialState(
                            pos=prev_after.pos | outcome.obs_after.pos,
                            neg=prev_after.neg | outcome.obs_after.neg,
                        )
                        prefix_cache[nxt_key] = merged_after
                        patched = StepOutcome(
                            outcome.action,
                            outcome.applicable,
                            merged_before,
                            merged_after,
                            outcome.goal_reached,
                        )
                        vspace.observe_step(patched)
                    else:
                        vspace.observe_step(outcome)

                    if not outcome.applicable:
                        break
                    prefix.append(ga)
                    pred_state = cur_domain.actions[ga[0]].successor(pred_state, ga[1])
                    if outcome.goal_reached:
                        prob_solved = True
                        break

                if prob_solved:
                    if used_relax:
                        confirmed_prior = tentative_prior
                        relax_accepts += 1
                elif not budget_hit:
                    if used_relax or env.mode != ObservationMode.PARTIAL:
                        nxt_dom = project_domain(confirmed_prior, vspace, self.tie_break)
                        if used_relax or write_domain(nxt_dom) == sig:
                            vspace.refuted_domains.add(sig)
                    else:
                        unchanged_streak = unchanged_streak + 1 if sig == prev_sig else 1
                        prev_sig = sig
                        if unchanged_streak >= 3:
                            vspace.refuted_domains.add(sig)

            steps_used += env.steps_used
            solved_flags.append(prob_solved)

        final_domain = project_domain(confirmed_prior, vspace, self.tie_break)
        return RepairResult(
            repaired_domain=final_domain,
            solved_training=tuple(solved_flags),
            steps_used=steps_used,
            episodes=episodes,
            planner_calls=planner_calls,
            relaxation_accepts=relax_accepts,
            trace=tuple(trace),
        )

    def repair_single(
        self, prior_domain: Domain, problem: Problem, env: Environment, planner: Planner
    ) -> RepairResult:
        return self.run(
            prior_domain, [problem], lambda _p, _b: env, planner, total_step_budget=env.step_budget
        )
