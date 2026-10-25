---
name: symbolic-world-model-laboratory
description: Explore, formalize, parse, and translate across diverse AI world model paradigms (STRIPS, SAS+, FOND, Numeric PDDL 2.1, Inductive Logic Programming / ASP, and Code World Models). Use when analyzing action schemas, computing state invariants, extracting causal graphs or landmarks, designing cross-paradigm translations, or formalizing discrete/symbolic transition systems.
metadata:
  model: inherit
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 🌐 Symbolic World Model Laboratory

A comprehensive, paradigm-agnostic research skill for modeling, analyzing, transforming, and verifying discrete, symbolic, and hybrid world models in Artificial Intelligence and Automated Planning.

---

## 1. Scope & Theoretical Foundations

In AI and Automated Planning, an environment is abstracted into a formal **World Model** characterizing state transitions, preconditions, side effects, and invariants. This skill supports the complete landscape of formal action representations:

### Supported Paradigms
1. **Classical Propositional & Lifted STRIPS / ADL**:
   - Signature: $\Sigma = (\mathcal{P}, \mathcal{A}, \mathcal{O}, \mathcal{T})$, where $\mathcal{P}$ is relational predicates, $\mathcal{A}$ lifted action schemas, $\mathcal{O}$ typed objects, $\mathcal{T}$ type hierarchy.
   - Action schema: $a = (\text{params}(a), \text{pre}(a), \text{add}(a), \text{del}(a))$.
   - First-order quantifiers ($\forall, \exists$) and conditional effects in ADL.

2. **Finite-Domain State-Variable Representation (SAS+)**:
   - Variables $V = \{v_1, \dots, v_n\}$ with discrete finite domains $\mathcal{D}(v)$.
   - States as total valuations $s \in \prod_{v \in V} \mathcal{D}(v)$.
   - Operators with prevail conditions $\text{prev}(o)$ and pre-post transitions $(v, \text{pre}_v \to \text{post}_v)$.
   - Mutual exclusion (mutex) cliques and invariant groups: $\sum_{p \in M} [p \in s] \le 1$.

3. **Fully Observable Non-Deterministic (FOND) & MDP Abstractions**:
   - Operators with non-deterministic effect sets: $\text{eff}(a) = \{E_1, E_2, \dots, E_k\}$.
   - Strong and strong-cyclic policy synthesis under environmental uncertainty.

4. **Numeric & Hybrid World Models (PDDL 2.1 Level 2/3)**:
   - State variables: Real-valued fluents $f \in \mathbb{R}$.
   - Linear and non-linear numeric conditions: $(\ge (\text{fuel} \ ?v) \ 10)$.
   - Continuous effects and assignment operators: $(\text{decrease} \ (\text{fuel} \ ?v) \ (\text{consumption} \ ?v))$.

5. **Inductive Logic Programming (ILP) & Answer Set Programming (ASP)**:
   - Logic programs with stable model semantics (clingo/Gringo).
   - Horn clauses, integrity constraints, and mode declarations for inductive learning (FastLAS, ILASP, Aleph).
   - Event calculus and transition rules: $\text{holds}(F, T+1) \leftarrow \text{action}(A, T), \text{causes}(A, F)$.

6. **Code-as-World-Models (Executable Simulators)**:
   - Programmatic state transition functions written in Python, Domain-Specific Languages (DSL), or Gym environments.
   - LLM-synthesized code world models (e.g. WorldCoder, Martín 2026).

---

## 2. When to Use This Skill

- When formalizing a new domain, game environment, or problem task into a symbolic world model.
- When inspecting or validating action schemas, precondition-effect consistency, or type hierarchies.
- When computing formal domain invariants: mutex groups, $h^2$ invariants, SAS+ finite domains.
- When constructing or inspecting causal graphs $CG(\Pi)$ and landmark graphs $LG(\Pi)$.
- When converting between paradigms (e.g., grounding STRIPS to SAS+, translating PDDL to ASP facts/rules, or compiling simulator code into PDDL operators).
- When investigating structural properties (e.g., domain reachability, reversible actions, dead-end states).

## Do Not Use This Skill When
- Solely measuring search-tree heuristic performance or node expansion explosions (use `search-space-topology-analyst`).
- Running the iterative online counterexample repair loop (use `counterexample-guided-rule-repair`).
- Auditing manuscript empirical claims against raw benchmark JSONs (use `scientific-theory-and-paper-architect`).

---

## 3. Mathematical Invariants & Formal Properties

### A. Precondition-Delete Effect Coherence (Prevail / Pre-Post Invariant)
In physical reality, an action cannot delete a property that was not previously true. For any well-formed SAS+ operator:
$$\forall (v, \text{pre}_v \to \text{post}_v) \in \text{prepost}(o): \quad \text{pre}_v \in \text{pre}(o)$$
In STRIPS notation:
$$p \in \text{del}(a) \implies p \in \text{pre}(a) \quad \text{or} \quad \exists q \text{ s.t. } \text{mutex}(p, q) \land q \in \text{pre}(a)$$
Any learned or mutated action model that violates this coherence condition is ill-formed and introduces ungrounded transition dynamics.

### B. Causal Graph $CG(\Pi)$
Let $V$ be the state variables of planning task $\Pi$. The causal graph is a directed graph $CG = (V, E)$ where $(u, v) \in E$ iff there exists an operator $o$ such that:
1. $u \in \text{vars}(\text{pre}(o)) \cup \text{vars}(\text{prepost}(o))$ and $v \in \text{vars}(\text{prepost}(o))$, or
2. $u, v \in \text{vars}(\text{prepost}(o))$ with $u \neq v$.

Acyclic or weakly coupled causal graphs permit polynomial-time subproblem decomposition and factored planning.

### C. Fact Landmarks & Action Landmarks
- A fact landmark $L \subseteq \mathcal{P}$ is a formula that must be true at some point in every valid execution plan $\pi$:
  $$\forall \pi = \langle a_1, \dots, a_k \rangle \text{ s.t. } s_0 \xrightarrow{\pi} s_* \in S_G, \quad \exists t \in \{0, \dots, k\}: s_t \models L$$
- Landmarks serve as admissible heuristic estimators ($h^{\text{LM-Cut}}$) and guides for domain verification.

---

## 4. Standard Operational Workflow

### Step 1: Paradigm Identification & Schema Intake
- Identify the target representation (STRIPS, SAS+, FOND, PDDL 2.1, ASP, or Code).
- Verify syntactic compliance (balanced parentheses, valid parameter types, consistent variable binding).

### Step 2: Invariant & Mutex Group Discovery
- Ground relational actions over object universe $\mathcal{O}$.
- Compute pairwise mutual exclusion ($h^2$ reachability analysis):
  $$\forall p, q: \quad h^2(\{p, q\}) = \infty \implies \text{mutex}(p, q)$$
- Partition propositions into maximal cliques $M_1, \dots, M_k$ to construct finite-domain SAS+ variables.

### Step 3: Semantic Well-Formedness & Coherence Audit
- Check each action schema $a \in \mathcal{A}$ against:
  1. *Parameter Coverage*: Every variable in $\text{pre}(a) \cup \text{add}(a) \cup \text{del}(a)$ must appear in $\text{params}(a)$.
  2. *Contradiction Freedom*: $\text{add}(a) \cap \text{del}(a) = \emptyset$ (or well-defined add-after-delete priority).
  3. *Pre-Post Coherence*: Verify that every deleted fluent has a causal justification in preconditions.

### Step 4: Cross-Paradigm Compilation (When Needed)
- **STRIPS $\to$ SAS+**: Execute Fast Downward translator (`translate/translate.py`) to extract SAS+ file, causal graph, and mutexes.
- **STRIPS $\to$ ASP**: Compile action schemas into choice rules, frame axioms, and goal constraints for Answer Set Solvers (`clingo`).
- **Code Simulator $\to$ PDDL**: Extract state variable signatures and action step functions into symbolic lifted predicates and deterministic effect lists.

### Step 5: Baseline Solvability Preflight
- Execute a reference planner (e.g., Fast Downward with `astar(blind())` or `astar(lmcut())`) on reference problems to confirm that the formal model admits valid plans before launching downstream experiments.

---

## 5. Verification Checklist & Anti-Hallucination Guardrails

- [ ] **No Guessing of Syntax**: Never generate non-standard PDDL requirements (e.g. do not invent `:continuous-time` without PDDL+ engine).
- [ ] **Lowercase Normalization**: In PDDL, all predicate names, type names, and objects must be lowercased to prevent Fast Downward lexical parsing errors.
- [ ] **Type Hierarchy Safety**: When `:typing` is declared, every object must have a valid supertype culminating in `object`.
- [ ] **Deterministic Tool Output**: Always verify model files via actual solver/translator compilation (`python -m pddl` or `translate.py`) rather than visual inspection.
