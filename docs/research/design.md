# Architecture and Experimental Design (`ammr/`)

## 1. Module Layout & Size Budget

Every module is strictly ≤ 300 lines (hard ceiling ≤ 800 lines) with single responsibility and no
circular imports:

```text
ammr/
  __init__.py          Package exports
  pddl/
    __init__.py
    sexp.py            S-expression parser & writer (~55 lines)
    model.py           Immutable Atom, Action, Domain, Problem, grounding, scrambling (~170 lines)
    io.py              Exact round-trip PDDL reader/writer (~195 lines)
  env.py               Isolated Environment + ObservationMode {binary, partial, full} (~130 lines)
  planner.py           Fast Downward (WSL /tmp) + pure-Python fallback planner (~165 lines)
  faults.py            Seeded random fault generator across Families A–D (~175 lines)
  repair/
    __init__.py
    hypotheses.py      Lifted candidate space + version-space constraints (~195 lines)
    update.py          Minimum-edit hitting-set projection & tie-breaking (~175 lines)
    loop.py            Closed-loop repair + planner-side unsolvability relaxation (~195 lines)
  baselines/
    __init__.py
    sam.py             Lifted SAM (offline & active goal-directed) (~145 lines)
    monotonic.py       Monotonic online precondition refinement from prior (~110 lines)
    random_probe.py    Fair random ground-action exploration + version-space repair (~115 lines)
  metrics.py           AMLGym-compatible syntactic, predictive, and solving metrics (~195 lines)
experiments/
  __init__.py
  run.py               Unified YAML-driven runner with manifest (git SHA, seeds, config) (~260 lines)
  analyze.py           Bootstrap 95 % CIs, paired Wilcoxon tests, markdown/LaTeX tables (~210 lines)
  claim_audit.py       Mechanical verification of documented claims against results JSON (~140 lines)
```

## 2. Formal Feedback & Isolation Contract (`ammr/env.py`)

`Environment` holds `_true_domain` privately. Learners receive `(prior_domain, problem, env)` only.
Let $\mathcal{G}$ be the ground-atom universe of `(prior_domain, problem)`. After executing ground
action $a(\vec{o})$ in true state $s$:

- If $s \models \text{Pre}_{M^*}(a(\vec{o}))$: `applicable = True`, $s' = \text{succ}_{M^*}(s, a(\vec{o}))$.
- Otherwise: `applicable = False`, $s' = s$ (no-op failure, matching AMLGym `RandomAgent`).

Each state $x \in \{s, s'\}$ is passed through observation channel $\mathcal{O}_{p_{\text{obs}}}$:

- `full` ($p_{\text{obs}} = 1$): `pos = x`, `neg = G \ x`.
- `partial(p)` ($0 < p < 1$): each $g \in \mathcal{G}$ is observed independently with probability $p$;
  `pos = x ∩ O`, `neg = O \ x`, and atoms in $\mathcal{G} \setminus O$ are **unobserved** (neither
  in `pos` nor in `neg`).
- `binary` ($p_{\text{obs}} = 0$): `pos = ∅`, `neg = ∅`. Zero state fluents leave `env.step()`.

## 3. Version-Space & Minimum-Edit Diagnosis (`ammr/repair/`)

For each action schema $a(?v_1, \dots, ?v_m)$, let $\mathcal{C}(a)$ be all type-compatible lifted
atoms over $a$'s parameters and domain constants with distinct variable arguments.

Given execution records $\mathcal{D}$:

1. **Positive step** $(\text{obs}_0, a(\vec{o}), \text{obs}_1)$ with injective binding $\vec{o}$:
   - Any $\alpha \in \mathcal{C}(a)$ with $\alpha[\vec{o}] \in \text{neg}_0$ is **forbidden** from `pre_pos(a)`.
   - Any $\alpha \in \mathcal{C}(a)$ with $\alpha[\vec{o}] \in \text{pos}_0$ is **forbidden** from `pre_neg(a)`.
   - Any $\alpha \in \mathcal{C}(a)$ with $\alpha[\vec{o}] \in \text{neg}_1$ is **forbidden** from `add(a)`;
     if also $\alpha[\vec{o}] \in \text{pos}_0$, then $\alpha$ is **forced** into `delete(a)`.
   - Any $\alpha \in \mathcal{C}(a)$ with $\alpha[\vec{o}] \in \text{pos}_1$ is **forbidden** from `delete(a)`;
     if also $\alpha[\vec{o}] \in \text{neg}_0$, then $\alpha$ is **forced** into `add(a)`.

2. **Negative step** $(\text{obs}_0, a(\vec{o}), \bot)$:
   - Generates conflict clause
     $$C = \{+\alpha \mid \alpha[\vec{o}] \notin \text{pos}_0\} \cup \{-\alpha \mid \alpha[\vec{o}] \notin \text{neg}_0\}.$$
   - Every consistent model must include at least one literal from $C$ in $\text{Pre}(a)$.
   - Under `binary` feedback ($\text{pos}_0 = \text{neg}_0 = \emptyset$), the learner tracks its
     predicted state $\hat{s}_t$ from known $s_0$ via $\widehat{M}$'s effects to form provisional
     conflicts; if a provisional conflict becomes unsatisfiable against positive observations, it is
     discarded because an upstream action's effect in $\widehat{M}$ diverged from $M^*$.

3. **Minimum-Edit Projection**:
   - Effects take the unique schema closest in symmetric difference to $(\text{add}_0(a), \text{delete}_0(a))$
     satisfying all forced/forbidden sets.
   - Preconditions keep all non-forbidden literals of $\text{Pre}_0(a)$ and add a **minimum-cardinality
     hitting set** covering all remaining unsatisfied conflicts $C$. Ties among equal-cardinality
     hitting sets are broken either lexicographically (`tie_break="lex"`, pure MBD) or by STRIPS
     delete-coherence (`tie_break="coherence"`), tested directly in ablation.

4. **Planner-Side Relaxation on Unsolvable Tasks**:
   - When `plan(M_t, P)` returns unsolvable, candidate 1-edit (then 2-edit) relaxations consistent
     with $\mathcal{D}$ (dropping an unforced prior precondition, dropping an unforced prior delete,
     or adding an unforbidden add effect) are checked with the planner (`0` environment steps).
   - Once a consistent relaxation yields a plan $\pi'$, executing $\pi'$ in `env` either confirms
     the relaxation via a positive transition (permanently updating $\mathcal{V}(\mathcal{D})$) or
     refutes it via a real counterexample.
