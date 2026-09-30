# Theoretical Foundations, Problematization & Research Gaps in Lightweight Symbolic Action Model Learning (2008–2026)

> **Document Type**: Scientific Research OS Theoretical Synthesis & Problematization Audit  
> **Status**: Curated Academic Reference  
> **Domain**: Symbolic Game AI, Action Model Learning, PDDL Synthesis, Inductive Logic Programming (ILP)  
> **Target Venues**: IEEE Transactions on Games (IEEE ToG), Artificial Intelligence Journal (AIJ), AAAI/ICAPS  

---

## 1. Executive Summary & Epistemic Realignment

In accordance with strict scientific methodology, we eliminate all dependencies on large language models (LLMs) and deep neural network black-boxes. Instead, we perform a first-principles theoretical investigation into **Lightweight Symbolic Action Model Learning**—a well-grounded, 100% deterministic, CPU-native paradigm spanning 18 years of literature (2008–2026).

This document audits the mathematical assumptions, theoretical boundaries, and unexamined research gaps when learning symbolic world models (e.g., PDDL action schemas, finite-state machine fluents, rule ASTs) directly from execution traces under **Minimal Rule Interventions**.

```mermaid
flowchart TD
    subgraph Execution Trace Data D
        T1["State-Action-State' Traces: (s_0, a_1, s_1, a_2, s_2, ...)"]
    end

    subgraph Symbolic Action Model Learner (Non-LLM)
        L1["LOCM / LOCM2 (Object State Machines)"]
        L2["SAM / ARMS (SAT/MAX-SAT PDDL Synthesis)"]
        L3["Inductive Logic Programming (Popper / FastLAS / ILP)"]
    end

    subgraph Learned Symbolic World Model
        M1["Learned Action Schema T_hat<br/>Preconditions P(a), Effects E(a)"]
    end

    subgraph Theoretical Failure Modes under Rule Interventions
        F1["Omitted Rare Precondition Gate"]
        F2["Unobserved Hidden State Variables (Latent Fluents)"]
        F3["Disjunctive Precondition Collapse"]
    end

    Execution Trace Data D --> Symbolic Action Model Learner (Non-LLM)
    Symbolic Action Model Learner (Non-LLM) --> Learned Symbolic World Model
    Learned Symbolic World Model --> Theoretical Failure Modes under Rule Interventions
```

---

## 2. 18-Year Literature Lineage of Symbolic Action Model Learning (2008–2026)

To ensure zero historical blindspots, we trace the foundational algorithms that infer action dynamics from observation traces without neural parameters:

| Algorithm / Paradigm | Primary Citation | Input Data Requirements | Core Mechanism | Theoretical Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **LOCM / LOCM2** | Cresswell et al. (ICAPS 2009, AIJ 2013) | Action sequences only (no state fluents required) | Finite State Automata (FSA) induction over object transitions | Cannot learn disjunctive preconditions or non-local spatial interactions. |
| **ARMS** | Yang et al. (IEEE TKDE 2007) | Partial state traces + plan instances | Weighted MAX-SAT constraint satisfaction | Requires known predicate definitions; sensitive to missing state fluents. |
| **SAM / AROMA** | Amir & Chang (AIJ 2008) | Full state fluents $(s, a, s')$ | Exact logical constraint filtering per action | Assumes complete deterministic observability; collapses under noise. |
| **ILP Rule Mining (Popper / FastLAS)** | Cropper & Dumančić (IJCAI 2021, AIJ 2023) | Positive / Negative execution traces + Background Knowledge | Answer Set Programming (ASP) & Hypothesize-and-Refute | High combinatorial search cost when background predicates grow. |
| **GGP Rule Induction** | Stephens & Such (IEEE ToG 2016), Gebser et al. (2018) | GDL / PuzzleScript AST transition diffs | Inductive pattern extraction over grid cellular automata | Fails zero-shot when new unobserved rule intervention branches occur. |

---

## 3. Problematization & Assumption Audit (Sandberg & Alvesson 2011)

In classical literature, symbolic action model learners are evaluated primarily on **Schema Reconstruction Accuracy** (matching ground-truth PDDL predicates) or **Passive Transition Prediction**. We conduct a formal Assumption Audit to expose why these metrics obscure planning failures:

### Assumption 1: Full Fluent Observability (The Transparency Assumption)
* **The Assumption**: Algorithms like SAM, LOCM, and ARMS take for granted that every state variable relevant to an action's precondition is explicitly recorded in state trace $s_t$.
* **The Problematization**: Under minimal rule interventions, environments introduce *latent fluents* (e.g., an internal counter, a hidden toggle switch, a non-local spatial dependency).
* **Consequence**: When a latent fluent is unobserved, the symbolic learner merges distinct physical states into a single state node, creating an **inconsistent FSA** that generates impossible plan steps.

### Assumption 2: Transition Accuracy $\implies$ Search Tree Topology Stability
* **The Assumption**: If a learned symbolic model $\hat{T}$ correctly predicts transitions across $99\%$ of sampled state-action pairs in training traces $D$, it is assumed fit for domain planning.
* **The Problematization**: In graph search (BFS / A*), a single missing precondition predicate in $\hat{T}$ creates spurious directed edges in the transition graph $G_{\hat{T}}$.
* **Consequence**: The search algorithm traverses non-existent shortcuts ("phantom paths"), causing **100% Play Regret** during execution on the true environment $G_T$, despite near-perfect passive accuracy.

---

## 4. Formal Mathematical Framework & Estimands

Let an environment be a Deterministic Factored Transition System:
$$\mathcal{M} = \langle S, A, T, s_0, S_G \rangle$$
where $S \subseteq 2^{\mathcal{F}}$ is the set of states composed of Boolean fluents $\mathcal{F}$, $A$ is the set of actions, $T: S \times A \to S \cup \{\bot\}$ is the transition function, $s_0$ is the initial state, and $S_G$ is the goal state set.

### 4.1. Learned Symbolic Schema Representation
A symbolic action schema for action $a \in A$ is defined as a tuple:
$$\hat{\Sigma}(a) = \langle \text{Pre}(a), \text{Eff}^+(a), \text{Eff}^-(a) \rangle$$
where $\text{Pre}(a) \subseteq \mathcal{F}$ are preconditions, $\text{Eff}^+(a)$ are add-effects, and $\text{Eff}^-(a)$ are delete-effects.

### 4.2. Rule Intervention Distance ($\Delta DSL$)
Let $\mathcal{M}$ be the base domain and $\mathcal{M}' = do(T \to T')$ be the interventional domain. The intervention distance $\Delta DSL(\mathcal{M}, \mathcal{M}')$ is the minimal tree edit distance between their formal rule ASTs:
$$\Delta DSL(\mathcal{M}, \mathcal{M}') = \text{TreeEditDistance}(\text{AST}(T), \text{AST}(T'))$$

### 4.3. The Planning Adequacy Estimand
Let $\pi^*_{\hat{T}}(s_0)$ be the plan generated by an optimal search agent navigating the learned symbolic model $\hat{T}$. The **Play Regret** $R_{\text{play}}$ on the true interventional environment $\mathcal{M}'$ is:
$$\text{Regret}_{\text{play}}(\hat{T}, \mathcal{M}') = \text{Cost}_{\mathcal{M}'}\left(\text{Execute}\left(\pi^*_{\hat{T}}(s_0)\right)\right) - \text{Cost}_{\mathcal{M}'}\left(\pi^*_{\mathcal{M}'}(s_0)\right)$$

Where $\text{Cost} = \infty$ if the plan fails to reach $S_G$.

---

## 5. Formal Research Questions (RQs) & Theoretical Hypotheses for Paper 1

### RQ1 (Symbolic Model Degradation under Rule Interventions)
> *How does the tree edit distance of a minimal rule intervention $\Delta DSL(\mathcal{M}, \mathcal{M}')$ degrade the schema reconstruction accuracy versus the active play success of lightweight symbolic action learners (LOCM, ARMS, ILP)?*

* **Hypothesis H1.1**: Passive schema accuracy degrades linearly with $\Delta DSL$, whereas active play success exhibits a sharp non-linear threshold collapse (step-function drop to 0% success) as soon as $\Delta DSL$ modifies a causal bottleneck fluent.

### RQ2 (Active Tree Search Counterexample Sample Complexity)
> *What is the minimal active exploration sample complexity $K_{\text{CEGIS}}$ required by a symbolic learner to eliminate phantom transition paths under sparse rule modifications?*

* **Hypothesis H2.1**: Passive trace sampling requires exponential samples $\mathcal{O}(2^{|\mathcal{F}|})$ to discover omitted rare preconditions, whereas Counterexample-Guided Active Tree Search bounds sample complexity to polynomial $\mathcal{O}(k \cdot \text{depth}(G_T))$, where $k$ is the number of modified AST rules.

---

## 6. Next Steps for Theoretical Refinement (No Code Written)

1. **Formal Proof Outline for Hypothesis H2.1**: Formalize the PAC (Probably Approximately Correct) active learning bound for symbolic action schemas under bounded AST modifications.
2. **Taxonomy Matrix of Symbolic Action Learners**: Complete a detailed comparison mapping LOCM, SAM, FastLAS, and AST-Pattern Learners against specific game rule intervention types.
3. **Paper 1 (IEEE ToG) Structural Outline**: Organize Sections I to IV of the manuscript around this non-LLM, symbolic foundation.
