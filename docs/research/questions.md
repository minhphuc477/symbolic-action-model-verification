# Research questions and honest positioning (rebuild draft v1)

## Setting

An agent is given a PDDL domain `M̂` that is *almost* right (hand-written with mistakes, or generated
by an LLM) and can act in an environment whose true dynamics follow an unknown domain `M*`.
`M̂` and `M*` differ in `k` atomic edits (add/remove a precondition or effect literal in an action
schema). The agent wants to solve planning tasks; it can plan with `M̂` and execute actions in the
environment.

**Feedback contract** (the legacy code violated this; the rebuild makes it explicit and
experimental):

| Mode | What the environment returns after executing ground action `a` in state `s` |
|---|---|
| `binary` | only whether `a` was applicable. Nothing about the state. |
| `partial` | applicability + the next state with each fluent hidden independently with probability `1 - p`. |
| `full` | applicability + the complete next state. |

## What is already known (see `literature.md`)

- Given a valid plan, a minimal repair can be computed offline (Lin et al. 2023).
- Given positive and negative plans, an optimal repair can be computed offline (Lin et al. 2025).
- Missing effects that make a task unsolvable can be repaired offline by compilation
  (Gragera et al. 2023).
- Passive policies cannot expose spurious preconditions; diagnostic actions can
  (Patel & Bukkapatnam).
- Models can be learned online from scratch (OLAM) or offline from traces (SAM, OffLAM).

## Open point we target

All offline repair methods take the evidence (plans, traces) as input. They do not say how an
agent should *produce* that evidence through interaction, or how much interaction is needed under
weaker feedback. Learning-from-scratch methods ignore the prior `M̂`.

**Candidate contribution (to be confirmed or rejected by the experiments, not assumed):**
a closed-loop procedure that uses `M̂` as a prior, plans with it, executes, and turns
(i) execution failures and (ii) planner unsolvability into evidence for a repair, and an empirical
characterisation of its interaction cost under the three feedback modes compared with
(a) learning from scratch and (b) random exploration followed by the same repair step.

If the experiments show that random exploration + offline repair is as cheap as the closed loop,
we report that as the finding.

## Research questions

- **RQ1 (diagnosis).** For sparse edits `k ∈ {1,2,3}`, how well does a model's one-step
  prediction accuracy on observed transitions predict whether plans computed with it succeed in the
  environment? *Measured:* prediction accuracy vs. plan execution success; rank correlation over
  randomly generated faults.
- **RQ2 (interaction cost).** How many environment steps does each method need to reach a model
  whose plans succeed on held-out tasks, under `binary`, `partial(p)`, and `full` feedback?
- **RQ3 (over-constrained models).** For edits that make tasks unsolvable in `M̂`
  (spurious preconditions, missing add effects), how often can a repair be found by planner-side
  relaxation search alone, and how many environment steps are needed to confirm it?
- **RQ4 (dependence on names).** Do results change when predicate and action names are replaced by
  meaningless identifiers? (Expected: no, for purely symbolic methods; tested, not assumed.)

## Hypotheses (falsifiable)

- **H1.** Prediction accuracy ≥ 0.95 does not imply plan success: there exist random single edits
  with accuracy ≥ 0.95 and plan success 0. *Falsified if* every fault with accuracy ≥ 0.95 also has
  plan success ≥ 0.9.
- **H2.** Under `full` feedback the closed loop needs fewer environment steps than OLAM-from-prior
  and random-exploration+repair at equal final success. *Falsified if* the median step count is not
  lower with a 95 % bootstrap CI excluding zero difference.
- **H3.** Under `binary` feedback the closed loop still reaches success on ≥ 80 % of single-edit
  faults within the step budget. *Falsified if* below 80 %.

## Evaluation protocol (fixed before running)

- Domains: IPC domains from the Fast Downward benchmark collection (fetched, not hand-written),
  plus the three game-style domains already in `domains/`, clearly labelled as ours.
- Faults: generated uniformly at random from all applicable edits with a recorded seed; never
  hand-picked. Faults that leave `M̂ == M*` semantically are discarded and counted.
- Tasks: each fault is evaluated on several problems; success is measured on held-out problems not
  used during repair.
- Seeds: ≥ 5 per configuration. Report medians, IQR, and bootstrap 95 % CIs.
- Every number in the thesis is produced by `experiments/` and checked by an audit script.
