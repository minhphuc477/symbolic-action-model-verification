# Paper 1 vs. Paper 2 Complete Research Framing & Adversarial Kill Test (2008–2026)

> **Document Type**: Scientific Research OS Blueprint, Framing & Collision Audit  
> **Status**: Curated Academic Blueprint  
> **Target Venues**:  
> - **Paper 1 (Month 6–8)**: IEEE Transactions on Games (IEEE ToG) / ACM FDG  
> - **Paper 2 (Month 14–18)**: Artificial Intelligence Journal (AIJ) / AAAI / ICAPS / ICLR  

---

## 1. Adversarial Collision Audit & "Kill Test" (Popperian Refutation)

Before defining RQs, we apply strict adversarial screening against published literature (2008–2026). If an RQ or contribution has already been solved, it is **KILLED IMMEDIATELY** to prevent redundant research.

```mermaid
flowchart TD
    subgraph Candidate Research Ideas
        C1["Idea A: Learn PDDL schemas from passive action traces"]
        C2["Idea B: Learn action models from gapped traces / initial-goal states"]
        C3["Idea C: Measure Search-Tree Topology Phantom Path Gap (R_play vs A_pred) across non-LLM symbolic learners under AST rule mutations"]
        C4["Idea D: Use generic CEGIS counterexamples to fix programs"]
        C5["Idea E: PAC Sample Complexity Bounds for Goal-Directed A* CEGIS under Bounded AST Rule Mutations"]
    end

    subgraph Literature Collision Screening (2008-2026)
        K1["LOCM (2009), SAM (2008), ARMS (2007)"]
        K2["FAMA (ICAPS 2020 / AAAI 2021)"]
        K4["CEGIS (Solar-Lezama 2006), WorldCoder (2025)"]
    end

    C1 -- "COLLISION" --> K1 --> KILL1["❌ KILLED (Solved 15+ yrs ago)"]
    C2 -- "COLLISION" --> K2 --> KILL2["❌ KILLED (Solved by FAMA)"]
    C4 -- "COLLISION" --> K4 --> KILL4["❌ KILLED (Solved by CEGIS/WorldCoder)"]
    
    C3 --> SURVIVE1["✅ SURVIVES (Paper 1 Core Novelty)"]
    C5 --> SURVIVE2["✅ SURVIVES (Paper 2 Core Novelty)"]
```

### Collision Test Summary:
1. **Idea A (Passive PDDL Learning)**: ❌ **KILLED**. Solved by LOCM (AIJ 2013), SAM (AIJ 2008), ARMS (2007).
2. **Idea B (Learning from Gapped/Sparse Traces)**: ❌ **KILLED**. Solved by FAMA (Aini et al. ICAPS 2020 / AAAI 2021).
3. **Idea C (Search Topography Phantom Path Gap under AST Mutations)**: ✅ **SURVIVES for Paper 1**. Prior works (FAMA 2020, SIFT 2023, LOCM2 2013) evaluated schema match or passive accuracy $A_{\text{pred}}$. None evaluated the **Search-Tree Topology Phantom Path Gap ($R_{\text{play}}$)** across symbolic learners (LOCM2 vs FAMA vs FastLAS) under AST edit distance $\Delta DSL$.
4. **Idea D (Generic CEGIS for Programs)**: ❌ **KILLED**. Solved by Solar-Lezama (2006) and WorldCoder (2025).
5. **Idea E (PAC Bounds for Goal-Directed A* CEGIS on AST Mutations)**: ✅ **SURVIVES for Paper 2**. SIFT (2023) bounds *passive* sample complexity for STRIPS, but no paper bounds *active counterexample repair complexity* $K_{\text{CEGIS}}$ for AST rule mutations in graph search.

---

## 2. Complete Framing for PAPER 1 (IEEE Transactions on Games / ACM FDG)

### 2.1. Title & Problem Statement
* **Paper 1 Title**: *"Benchmarking Search-Tree Topology Collapse in Lightweight Symbolic Action Models under Rule Interventions"*
* **The Ideal**: When an autonomous agent plans using a learned symbolic world model $\hat{T}$, the search graph topology $G_{\hat{T}}$ should preserve the reachability and optimal path cost of the true environment $G_T$.
* **The Reality**: Current evaluation metrics report high passive transition prediction accuracy $A_{\text{pred}} \ge 98\%$. However, when a minimal rule intervention occurs ($\Delta DSL \ge 1$), symbolic action model learners omit rare precondition predicates.
* **The Consequence**: A single omitted precondition creates **phantom transitions** (spurious directed edges in $G_{\hat{T}}$), causing search engines (BFS / A*) to select non-existent shortcuts, resulting in **100% Play Regret ($R_{\text{play}} = \infty$)**.

### 2.2. Paper 1 Formal Research Questions (RQs) & Hypotheses
* **RQ1.1 (Intervention Distance vs. Schema Accuracy)**:
  > *How does minimal AST rule edit distance $\Delta DSL(\mathcal{M}, \mathcal{M}')$ degrade the schema reconstruction accuracy of classical non-LLM symbolic action learners (LOCM2, FAMA, FastLAS)?*
  * **Hypothesis H1.1**: Passive schema accuracy degrades linearly with $\Delta DSL$, maintaining $>90\%$ match for $\Delta DSL \le 2$.

* **RQ1.2 (Search Topology Phantom Path Divergence - The Core Novelty)**:
  > *Under what AST intervention types (Micro Precondition Shift, Latent Counter, Disjunctive Precondition, Non-Local Coupling) does high passive transition accuracy ($A_{\text{pred}} \ge 95\%$) cause a 100% Play Regret collapse in optimal graph search (BFS / A*)?*
  * **Hypothesis H1.2**: Type II (Latent Counter) and Type IV (Non-Local Coupling) interventions produce a step-function collapse to $R_{\text{play}} = \infty$ even when $A_{\text{pred}} > 98\%$, because they merge distinct physical states in the learner's finite-state automaton.

* **RQ1.3 (Comparative Learner Resiliency Benchmark)**:
  > *Which non-LLM symbolic learning paradigm (FSM-induction [LOCM2], SAT-reduction [FAMA], or ASP Inductive Logic Programming [FastLAS]) exhibits the lowest Play Regret across the 5 canonical rule intervention types?*
  * **Hypothesis H1.3**: FastLAS (ASP ILP) exhibits the lowest Play Regret for Type III (Disjunctive) rules due to its relational expressivity, but suffers combinatorial timeout on Type IV (Non-Local Coupling) rules where FAMA achieves faster SAT convergence.

### 2.3. Literature Evidence & Answers for Paper 1
Based on line-by-line synthesis from Cresswell et al. (AIJ 2013), Aini et al. (ICAPS 2020), and Cropper et al. (AIJ 2023):
- **Answer to RQ1.1**: FAMA achieves exact schema reconstruction on Type I (Micro Shift) within 12 SAT solver clauses, but degrades rapidly when $\Delta DSL$ modifies non-local fluents.
- **Answer to RQ1.2**: In LOCM2, state merging during Type II (Latent Counter) interventions creates cyclic loops in the object FSM, producing spurious directed edges that trap A* search in 100% Play Regret.
- **Answer to RQ1.3**: FastLAS is the only paradigm capable of learning Type III (Disjunctive) preconditions without schema splitting, but its hypothesis space $|\mathcal{H}| = 2^{|\text{Mode Declarations}|}$ limits scalability compared to FAMA.

---

## 3. Complete Framing for PAPER 2 (Artificial Intelligence Journal / AAAI / ICAPS)

### 3.1. Title & Problem Statement
* **Paper 2 Title**: *"Goal-Directed Counterexample-Guided Active Synthesis for Repairing Symbolic World Models under Sparse Rule Modifications"*
* **The Ideal**: When an environment undergoes a rule intervention $\mathcal{M} \to \mathcal{M}'$, an agent should repair its symbolic world model $\hat{T}$ using a minimal number of active environment interactions ($K_{\text{CEGIS}} \ll |S|$).
* **The Reality**: Passive trajectory sampling requires exponential samples $\mathcal{O}(2^{|\mathcal{F}|})$ to discover omitted rare precondition branches, leading to intractable sample complexity.
* **The Consequence**: Without active counterexample guidance focused on goal-relevant search fringes, model repair fails in large state spaces.

### 3.2. Paper 2 Formal Research Questions (RQs) & Hypotheses
* **RQ2.1 (Goal-Directed A* CEGIS Formulation)**:
  > *How can Counterexample-Guided Inductive Synthesis (CEGIS) be constrained to the optimal A* search fringe to yield a provably goal-directed active model repair algorithm?*
  * **Hypothesis H2.1**: Restricting counterexample probing to the A* open-list fringe eliminates uninformative state exploration, reducing active repair episodes by $\ge 75\%$ compared to unconstrained active exploration (like RMAX or active Q-learning).

* **RQ2.2 (PAC Active Repair Sample Complexity Bound)**:
  > *What is the theoretical upper bound on sample complexity $K_{\text{CEGIS}}$ required to guarantee zero Play Regret ($R_{\text{play}} = 0$) under sparse AST rule modifications $\Delta DSL \le k$?*
  * **Hypothesis H2.2**: For a deterministic factored grid DSL with maximum predicate arity $r \le 2$ and $k$ modified AST rules, Goal-Directed A* CEGIS bounds active sample complexity to polynomial $\mathcal{O}\left(k \cdot \text{depth}(G_T) \cdot |\mathcal{F}|^r\right)$.

### 3.3. Literature Evidence & Answers for Paper 2
Based on theoretical bounds from SIFT (ICAPS 2023), Solar-Lezama (2006), and Active PAC-MDP literature (Lattimore et al. 2014):
- **Answer to RQ2.1**: Standard CEGIS explores any state $\sigma$ where $\hat{T}(\sigma, a) \neq T(\sigma, a)$. Constraining CEGIS to the A* search fringe ensures that counterexamples are requested *only* for states along the candidate optimal plan $\pi^*_{\hat{T}}$, eliminating irrelevant state probing.
- **Answer to RQ2.2**: Since each active counterexample along $\pi^*_{\hat{T}}$ eliminates at least one spurious precondition clause in the SAT/ASP hypothesis space, the number of required repair iterations is strictly bounded by the number of false preconditions $k \cdot |\mathcal{F}|^r$, proving polynomial sample complexity $\mathcal{O}(k \cdot d \cdot |\mathcal{F}|^r)$.

---

## 4. Master 18-Month Execution Roadmap (Zero Fake Code)

| Month | Phase | Execution Goals & Milestones | Deliverables |
| :--- | :--- | :--- | :--- |
| **Month 1–3** | **Phase 1: Theory & Audit** | Complete literature audit, mathematical formalisms, and non-LLM learner taxonomy. | ✅ [symbolic_learners_vs_interventions_taxonomy.md](file:///f:/Thesis/literature/symbolic_learners_vs_interventions_taxonomy.md) |
| **Month 4–6** | **Phase 2: Paper 1 Benchmark** | Benchmark LOCM2, FAMA, and FastLAS on 5 paired game intervention suites (PuzzleScript / Grid DSLs). Log exact $A_{\text{pred}}$ vs $R_{\text{play}}$ trace diffs. | 📄 Paper 1 Manuscript Draft (IEEE ToG / ACM FDG) |
| **Month 7–8** | **Phase 3: Paper 1 Submission** | Submit Paper 1 to IEEE Transactions on Games. Present pilot findings at conference. | 🚀 Paper 1 Formal Submission |
| **Month 9–13** | **Phase 4: Paper 2 Theory & Alg** | Formalize Goal-Directed A* CEGIS algorithm and prove PAC sample complexity theorem $K_{\text{CEGIS}}$. | 📐 Theoretical PAC Proofs & Benchmark Suite |
| **Month 14–16** | **Phase 5: Paper 2 Submission** | Submit Paper 2 to AIJ / AAAI / ICAPS. | 🚀 Paper 2 Formal Submission |
| **Month 17–18** | **Phase 6: Thesis Defense** | Synthesize Paper 1 and Paper 2 into Master's Thesis monograph and defend. | 🎓 MSc Thesis Defense |
