"""Fair random ground-action exploration followed by minimum-edit version-space repair."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from ammr.env import Environment, ObservationMode, PartialState, StepOutcome
from ammr.pddl.model import Domain, GroundAction, Problem, State, ground_actions, ground_universe
from ammr.repair.hypotheses import DomainVersionSpace
from ammr.repair.loop import RepairResult
from ammr.repair.update import TieBreak, project_domain


class RandomRepairBaseline:
    """Uniform random probing (never reading M*) + minimum-edit projection onto prior."""

    def __init__(self, seed: int = 0, episode_len: int = 25, tie_break: TieBreak = "lex") -> None:
        self.seed = seed
        self.episode_len = episode_len
        self.tie_break: TieBreak = tie_break

    def run(
        self,
        prior_domain: Domain,
        problems: Sequence[Problem],
        env_factory: Callable[[Problem, int], Environment],
        total_step_budget: int = 200,
    ) -> RepairResult:
        rng = random.Random(self.seed)
        vspace = DomainVersionSpace(prior_domain)
        trace: list[StepOutcome] = []
        solved_flags: list[bool] = []
        steps_used = 0
        episodes = 0
        n_probs = max(1, len(problems))

        for idx, prob in enumerate(problems):
            rem_total = total_step_budget - steps_used
            if rem_total <= 0:
                solved_flags.append(False)
                continue
            alloc = rem_total // (n_probs - idx)
            if alloc <= 0:
                solved_flags.append(False)
                continue
            env = env_factory(prob, alloc)
            ops = list(ground_actions(prior_domain, prob))
            univ = ground_universe(prior_domain, prob)
            prob_solved = False
            pred_state: State = prob.init
            prefix: list[GroundAction] = []

            if ops:
                while env.remaining_steps > 0:
                    if env.steps_used % self.episode_len == 0:
                        env.reset()
                        pred_state = prob.init
                        prefix = []
                        episodes += 1
                    ga = rng.choice(ops)
                    out = env.step(ga)
                    trace.append(out)
                    if env.mode == ObservationMode.BINARY:
                        fb = PartialState(pos=pred_state, neg=univ - pred_state)
                        vspace.observe_step(out, fallback_before=fb, provisional=bool(prefix))
                    else:
                        vspace.observe_step(out)
                    if out.applicable:
                        prefix.append(ga)
                        pred_state = prior_domain.actions[ga[0]].successor(pred_state, ga[1])
                    if out.goal_reached:
                        prob_solved = True

            steps_used += env.steps_used
            solved_flags.append(prob_solved)

        repaired = project_domain(prior_domain, vspace, tie_break=self.tie_break)
        return RepairResult(
            repaired_domain=repaired,
            solved_training=tuple(solved_flags),
            steps_used=steps_used,
            episodes=episodes,
            planner_calls=0,
            relaxation_accepts=0,
            trace=tuple(trace),
        )
