"""Lifted Safe Action Model (SAM) baseline (Juba, Le & Stern, KR 2021) + fair RandomAgent.

Follows AMLGym's ``RandomAgent`` contract: ground actions are sampled uniformly from the
type-valid groundings of ``(signature_domain, problem)`` without inspecting ``M*``; positive
injective transitions are then passed to lifted SAM.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from ammr.env import Environment, StepOutcome
from ammr.faults import lifted_atom_candidates
from ammr.pddl.model import Action, Domain, Problem, ground_actions, ground_atom
from ammr.repair.loop import RepairResult


def learn_sam_from_outcomes(signature_domain: Domain, outcomes: Sequence[StepOutcome]) -> Domain:
    """Learn a conservative lifted STRIPS action model from observed positive transitions."""
    allow_neg = ":negative-preconditions" in signature_domain.requirements
    cands_map = {
        name: set(lifted_atom_candidates(signature_domain, act))
        for name, act in signature_domain.actions.items()
    }
    pre_pos = {name: set(cands) for name, cands in cands_map.items()}
    pre_neg = {name: (set(cands) if allow_neg else set()) for name, cands in cands_map.items()}
    adds = {name: set() for name in signature_domain.actions}
    dels = {name: set() for name in signature_domain.actions}
    seen_pos = {name: False for name in signature_domain.actions}

    for out in outcomes:
        if not out.applicable:
            continue
        name, args = out.action
        # SAM requires injective parameter bindings to avoid lifted aliasing
        if len(set(args)) != len(args):
            continue
        act = signature_domain.actions[name]
        b = act.bind(args)
        seen_pos[name] = True
        for c in list(pre_pos[name]):
            if ground_atom(c, b) in out.obs_before.neg:
                pre_pos[name].discard(c)
        if allow_neg:
            for c in list(pre_neg[name]):
                if ground_atom(c, b) in out.obs_before.pos:
                    pre_neg[name].discard(c)
        for c in cands_map[name]:
            g = ground_atom(c, b)
            if g in out.obs_after.pos and g in out.obs_before.neg:
                adds[name].add(c)
            elif g in out.obs_after.neg and g in out.obs_before.pos:
                dels[name].add(c)

    learned_actions: dict[str, Action] = {}
    for name, act in signature_domain.actions.items():
        if not seen_pos[name]:
            # Unobserved actions keep maximally conservative preconditions and empty effects
            learned_actions[name] = Action(name, act.params, frozenset(cands_map[name]))
        else:
            learned_actions[name] = Action(
                name=name,
                params=act.params,
                pre_pos=frozenset(pre_pos[name]),
                pre_neg=frozenset(pre_neg[name] - pre_pos[name]),
                add=frozenset(adds[name]),
                delete=frozenset(dels[name] - adds[name]),
            )
    return Domain(
        name=signature_domain.name,
        requirements=signature_domain.requirements,
        types=signature_domain.types,
        constants=signature_domain.constants,
        predicates=signature_domain.predicates,
        actions=learned_actions,
    )


class RandomSAMBaseline:
    """AMLGym-style RandomAgent: uniform ground-action exploration + lifted SAM."""

    def __init__(self, seed: int = 0, episode_len: int = 25) -> None:
        self.seed = seed
        self.episode_len = episode_len

    def run(
        self,
        prior_domain: Domain,
        problems: Sequence[Problem],
        env_factory: Callable[[Problem, int], Environment],
        total_step_budget: int = 200,
    ) -> RepairResult:
        rng = random.Random(self.seed)
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
            prob_solved = False
            if ops:
                while env.remaining_steps > 0:
                    if env.steps_used % self.episode_len == 0:
                        env.reset()
                        episodes += 1
                    out = env.step(rng.choice(ops))
                    trace.append(out)
                    if out.goal_reached:
                        prob_solved = True
            steps_used += env.steps_used
            solved_flags.append(prob_solved)

        learned = learn_sam_from_outcomes(prior_domain, trace)
        return RepairResult(
            repaired_domain=learned,
            solved_training=tuple(solved_flags),
            steps_used=steps_used,
            episodes=episodes,
            planner_calls=0,
            relaxation_accepts=0,
            trace=tuple(trace),
        )
