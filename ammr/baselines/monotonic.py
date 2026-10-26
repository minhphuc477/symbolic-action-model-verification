"""Monotonic precondition-tightening baseline starting from ``prior_domain``.

Plans with the current model and tightens preconditions upon inapplicable steps via hitting
sets, without relaxing ``prior_domain`` preconditions, updating effects, or searching planner
relaxations on unsolvable tasks.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from ammr.env import Environment, ObservationMode, PartialState, StepOutcome
from ammr.faults import dynamic_predicates
from ammr.pddl.io import write_domain
from ammr.pddl.model import Action, Domain, GroundAction, Problem, State, ground_universe
from ammr.planner import Planner, PlanStatus
from ammr.repair.hypotheses import DomainVersionSpace, PreLit
from ammr.repair.loop import RepairResult
from ammr.repair.update import TieBreak, _rank_hitting_set, solve_min_hitting_sets


def _tighten_domain(
    prior_domain: Domain, vspace: DomainVersionSpace, tie_break: TieBreak = "lex"
) -> Domain:
    """Add minimum hitting-set preconditions while keeping all prior preconditions & effects."""
    dyn = dynamic_predicates(prior_domain)
    actions: dict[str, Action] = {}
    for name, prior_act in prior_domain.actions.items():
        hyp = vspace.actions[name]
        base_lits: set[PreLit] = {(True, a) for a in prior_act.pre_pos} | {
            (False, a) for a in prior_act.pre_neg
        }
        base_atoms = {a for _, a in base_lits}
        forb: set[PreLit] = {
            (True, a) for a in hyp.forbidden_pre_pos | hyp.prov_forbidden_pre_pos
        } | {(False, a) for a in hyp.forbidden_pre_neg | hyp.prov_forbidden_pre_neg}

        clauses: list[frozenset[PreLit]] = []
        for c in hyp.conflicts:
            if c.literals & base_lits:
                continue
            cand = frozenset(lit for lit in (c.literals - forb) if lit[1] not in base_atoms)
            if cand:
                clauses.append(cand)
        hsets = solve_min_hitting_sets(clauses, max_solutions=6)
        hsets.sort(
            key=lambda h: _rank_hitting_set(h, prior_act.add, prior_act.delete, dyn, tie_break)
        )
        merged = base_lits | hsets[0]
        actions[name] = Action(
            name=name,
            params=prior_act.params,
            pre_pos=frozenset(a for s, a in merged if s),
            pre_neg=frozenset(a for s, a in merged if not s),
            add=prior_act.add,
            delete=prior_act.delete,
        )
    return Domain(
        name=prior_domain.name,
        requirements=prior_domain.requirements,
        types=prior_domain.types,
        constants=prior_domain.constants,
        predicates=prior_domain.predicates,
        actions=actions,
    )


class MonotonicRepairBaseline:
    """Failure-driven monotonic precondition refinement without relaxation or effect repair."""

    def __init__(self, tie_break: TieBreak = "lex", planner_timeout_s: float = 10.0) -> None:
        self.tie_break: TieBreak = tie_break
        self.planner_timeout_s = planner_timeout_s

    def run(
        self,
        prior_domain: Domain,
        problems: Sequence[Problem],
        env_factory: Callable[[Problem, int], Environment],
        planner: Planner,
        total_step_budget: int = 200,
    ) -> RepairResult:
        vspace = DomainVersionSpace(prior_domain)
        steps_used = 0
        episodes = 0
        planner_calls = 0
        trace: list[StepOutcome] = []
        solved_flags: list[bool] = []

        for prob in problems:
            rem = total_step_budget - steps_used
            if rem <= 0:
                solved_flags.append(False)
                continue
            env = env_factory(prob, rem)
            univ = ground_universe(prior_domain, prob)
            prefix_cache: dict[tuple[GroundAction, ...], PartialState] = {}
            prob_solved = False
            prev_sig = ""
            unchanged = 0

            while env.remaining_steps > 0 and not prob_solved:
                cur_domain = _tighten_domain(prior_domain, vspace, self.tie_break)
                sig = write_domain(cur_domain)
                if sig == prev_sig:
                    unchanged += 1
                    if env.mode != ObservationMode.PARTIAL or unchanged >= 3:
                        break
                else:
                    unchanged = 0
                prev_sig = sig

                planner_calls += 1
                res = planner.solve(cur_domain, prob, self.planner_timeout_s)
                if res.status != PlanStatus.SOLVED:
                    break

                env.reset()
                episodes += 1
                if prob.goal_reached(prob.init):
                    prob_solved = True
                    break

                pred_state: State = prob.init
                prefix: list[GroundAction] = []
                for ga in res.plan:
                    if env.remaining_steps == 0:
                        break
                    out = env.step(ga)
                    trace.append(out)
                    pkey = tuple(prefix)
                    if env.mode == ObservationMode.BINARY:
                        fb = PartialState(pos=pred_state, neg=univ - pred_state)
                        vspace.observe_step(out, fallback_before=fb, provisional=bool(prefix))
                    elif env.mode == ObservationMode.PARTIAL:
                        prev = prefix_cache.get(pkey, PartialState())
                        mb = PartialState(
                            pos=prev.pos | out.obs_before.pos,
                            neg=prev.neg | out.obs_before.neg,
                        )
                        prefix_cache[pkey] = mb
                        vspace.observe_step(
                            StepOutcome(
                                out.action, out.applicable, mb, out.obs_after, out.goal_reached
                            )
                        )
                    else:
                        vspace.observe_step(out)
                    if not out.applicable:
                        break
                    prefix.append(ga)
                    pred_state = cur_domain.actions[ga[0]].successor(pred_state, ga[1])
                    if out.goal_reached:
                        prob_solved = True
                        break

            steps_used += env.steps_used
            solved_flags.append(prob_solved)

        return RepairResult(
            repaired_domain=_tighten_domain(prior_domain, vspace, self.tie_break),
            solved_training=tuple(solved_flags),
            steps_used=steps_used,
            episodes=episodes,
            planner_calls=planner_calls,
            relaxation_accepts=0,
            trace=tuple(trace),
        )
