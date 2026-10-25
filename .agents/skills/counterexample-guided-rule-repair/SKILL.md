---
name: counterexample-guided-rule-repair
description: Active counterexample-guided inductive synthesis, abduction, and repair engine for symbolic world models, logic rules, and action schemas. Use when resolving execution failures, repairing over-constrained or under-constrained PDDL models, executing zero-query offline backtracking, or ranking hypotheses via precondition-delete effect coherence.
metadata:
  model: inherit
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 🛠️ Counterexample-Guided Rule Repair (CEG-OMR)

A domain-independent, paradigm-agnostic research skill for repairing faulty, incomplete, drifted, or synthesized symbolic world models using active counterexamples and minimal-relaxation abduction.

---

## 1. Theoretical Framework & Fault Duality

Action model repair operates over the tension between two dual failure modes:

```
               ┌────────────────────────────────────────────────────────┐
               │         Initial Drifted / Synthesized Model M_0        │
               └───────────────────────────┬────────────────────────────┘
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 ▼                                                   ▼
   [OVER-APPROXIMATION FAULTS]                         [UNDER-APPROXIMATION FAULTS]
   • Omitted Preconditions                             • Spurious Preconditions
   • Spurious Add Effects                              • Missing Delete Effects
   • Symptoms: Phantom Shortcuts,                      • Symptoms: False Dead-Ends,
     Heuristic Seduction, Physical                       Planner Unsolvability (Exit 11),
     Execution Failure: (s_t, a_t, ⊥)                    Unreachable Goals
                 │                                                   │
                 ▼                                                   ▼
       Physical Counterexample                             Offline Abductive Search
       Driven Repair (Add Precondition)                    (Minimal Precondition Drop)
                 │                                                   │
                 └─────────────────────────┬─────────────────────────┘
                                           │
                                           ▼
                   ┌───────────────────────────────────────────────┐
                   │    Zero-Query Backtracking Filter (K_env = 0)  │
                   │    Validate Candidate M' via Internal Planner │
                   └───────────────────────┬───────────────────────┘
                                           ▼
                   ┌───────────────────────────────────────────────┐
                   │      Converged, Play-Adequate World Model     │
                   └───────────────────────────────────────────────┘
```

### A. Formal Fault Taxonomy
Given ground-truth model $\mathcal{M}^* = \langle \mathcal{P}, \mathcal{A}^*, I, G \rangle$ and imperfect model $\hat{\mathcal{M}} = \langle \mathcal{P}, \hat{\mathcal{A}}, I, G \rangle$:
1. **Family A (Omission / Over-approximation)**: $\exists a \in \mathcal{A}, \ p \in \text{pre}^*(a) \setminus \hat{\text{pre}}(a)$.
   - Creates spurious shortcuts. Manifests as physical execution failure: $\text{exec}(s_t, a_t) = \bot$.
2. **Family B (Spurious Constraint / Under-approximation)**: $\exists a \in \mathcal{A}, \ p \in \hat{\text{pre}}(a) \setminus \text{pre}^*(a)$.
   - Blocks legal trajectories. Manifests as planner unsolvability: $\Pi(\hat{\mathcal{M}}) = \text{UNSOLVABLE}$.
3. **Family C (Corrupted / Inverted Effect)**: $\exists a \in \mathcal{A}, \ p \in \text{add}^*(a) \land p \in \hat{\text{del}}(a)$.
   - Manifests as state divergence: $s_{t+1}^{\text{real}} \neq s_{t+1}^{\text{pred}}$.
4. **Family D (Compound Multi-Fault)**: Simultaneous coexistence of Families A, B, and C with drift size $k = \|\hat{\mathcal{M}} \ominus \mathcal{M}^*\|_1 \ge 2$.

---

## 2. Core Repair Principles

### Principle 1: Precondition-Delete Effect Coherence Ranking
To repair a physical execution failure $(s_t, a_t, \bot)$, the algorithm must identify which missing precondition $p^* \in \mathcal{P}$ caused the failure.
- *Naive search space*: $2^{|\mathcal{P}|}$ possible subsets.
- *Physical Invariant (Helmert 2009, Cresswell 2009)*: Actions that delete a state variable value almost universally require that value (or its mutual exclusion counterpart) as a precondition:
  $$p \in \text{del}(a) \implies p \in \text{pre}(a)$$
- *Ranking Function*: Rank candidate literals $p \in \mathcal{P} \setminus s_t$:
  $$\text{Score}(p, a) = w_1 \cdot \mathbb{I}(p \in \text{del}(a)) + w_2 \cdot \mathbb{I}(\exists q \in \text{del}(a): \text{mutex}(p, q)) + w_3 \cdot \text{Freq}(p \text{ in prior states})$$
  This prunes the candidate search space by orders of magnitude.

### Principle 2: Minimal-Relaxation Abduction
When the planner reports that goal $S_G$ is unsolvable under $\hat{\mathcal{M}}$ (under-approximation deadlock):
1. Compute the relaxed causal reachability of $S_G$.
2. Identify the bottleneck actions $a_{\text{blocked}}$ whose preconditions cannot be satisfied from $s_0$.
3. Find the minimal literal set $\Delta \subset \hat{\text{pre}}(a_{\text{blocked}})$ such that:
   $$\hat{\text{pre}}(a_{\text{blocked}}) \setminus \Delta \implies \text{Solvable}(\Pi)$$
   minimizing the syntactic edit distance $\|\Delta\|_1$.

### Principle 3: Offline Zero-Query Backtracking ($K_{\text{env}} = 0$)
Whenever a candidate repair $\mathcal{M}'$ is hypothesized:
- **Do NOT execute in the real environment immediately.**
- Invoke the internal planner on reference benchmark tasks with $\mathcal{M}'$.
- If $\mathcal{M}'$ renders previously solvable tasks unsolvable, or produces immediate causal deadlocks, refute $\mathcal{M}'$ internally without expending any real environment steps ($K_{\text{env}} = 0$).

---

## 3. When to Use This Skill

- When an agent encounters execution failures (`ExecutionFailedError`, `ActionPreconditionViolated`).
- When a planner outputs exit code 11 (unsolvable task) due to over-constrained action definitions.
- When repairing domain files with multi-fault drift (missing/spurious preconditions and effects).
- When benchmarking active model learning against passive baselines (FAMA, LOCM2, FastLAS, SAM).
- When validating sample complexity ($K_{\text{env}}$) and polynomial query bounds.

## Do Not Use This Skill When
- Solely parsing or syntax checking PDDL files without repair (use `symbolic-world-model-laboratory`).
- Plotting heuristic search-tree depth landscapes (use `search-space-topology-analyst`).
- Writing the final paper narrative (use `scientific-theory-and-paper-architect`).

---

## 4. Standard Operational Workflow

### Step 1: Counterexample Ingestion & Classification
Receive the observation tuple:
$$\tau = (s_t, a_t, s'_{t+1}, \text{status})$$
- If $\text{status} = \text{FAILED}$ (precondition violation): Classify as **Over-approximation (Family A)**.
- If $\text{status} = \text{UNSOLVABLE}$ (planner fails to find plan): Classify as **Under-approximation (Family B)**.
- If $\text{status} = \text{DIVERGENT}$ ($s'_{t+1} \neq \hat{T}(s_t, a_t)$): Classify as **Effect Mutation (Family C)**.

### Step 2: Hypothesis Generation & Coherence Scoring
- For Family A: Generate candidate preconditions from false literals in $s_t$:
  $$\mathcal{C} = \{p \in \mathcal{P} \mid s_t \not\models p\}$$
  Sort $\mathcal{C}$ by Precondition-Delete Coherence Score.
- For Family B: Run Minimal-Relaxation Abduction to identify candidate spurious literals in $\hat{\text{pre}}(a_t)$.

### Step 3: Offline Planner-Unsolvability Gate ($K_{\text{env}} = 0$)
For the top-ranked candidate hypothesis $H$:
1. Construct temporary domain $\mathcal{M}_H = \hat{\mathcal{M}} \oplus H$.
2. Call internal solver: `FastDownwardRunner.solve(domain=\mathcal{M}_H, problem=P)`.
3. If solver returns `UNSOLVABLE` on known reachable instances: Refute $H$, backtrack, and test the next candidate. No environment interaction consumed.

### Step 4: Active Online Validation
Once candidate passes the offline gate:
1. Re-plan to goal with $\mathcal{M}_H$.
2. Dispatch action sequence to physical environment.
3. If action executes successfully: Retain $H$, increment solved counter, update hypothesis space.
4. If action fails: Register new counterexample $(s_t', a_t', \bot)$ and iterate.

---

## 5. Anti-Hallucination & Verification Checklist

- [ ] **No Synthesizing Non-Existent Predicates**: Only hypothesize literals composed of valid domain predicates and matching action parameter types.
- [ ] **Preserve Static Invariants**: Never abduce a precondition that contradicts known domain types or static constants.
- [ ] **Track Exact Query Counts**: Maintain precise counts of $K_{\text{env}}$ (real environment steps) and $N_{\text{plan}}$ (planner calls). Never report fabricated sample efficiency.
