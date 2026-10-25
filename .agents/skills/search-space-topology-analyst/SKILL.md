---
name: search-space-topology-analyst
description: Graph-theoretic and heuristic topology analyzer for discrete state spaces, planning graphs, and heuristic search algorithms (A*, IDA*, GBFS). Use when diagnosing heuristic seduction, search-tree topology collapse, objective mismatch between 1-step prediction and plan execution, recognized vs unrecognized dead-ends, or branch divergence bounds.
metadata:
  model: inherit
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 📐 Search-Space Topology Analyst

An advanced mathematical and algorithmic research skill for rigorously analyzing discrete state-transition graphs, heuristic search spaces, and the topological pathologies that arise from imperfect or perturbed world models.

---

## 1. Mathematical Foundations & Graph Topologies

A deterministic discrete planning task defines an underlying **State Transition System** (directed graph):
$$TS = (S, E, s_0, S_G)$$
- **Vertices $S$**: The set of all reachable states valuation over state fluents.
- **Edges $E$**: Directed transitions $(s, a, s')$ where $a \in \mathcal{A}$, $s \models \text{pre}(a)$, and $s' = (s \setminus \text{del}(a)) \cup \text{add}(a)$.
- **Initial State $s_0 \in S$**, and **Goal States $S_G \subseteq S$**.

### A. Hoffmann's Local Search Topology (JAIR 2001 / 2005)
Heuristic search landscapes (under $h_{\text{FF}}, h^{\text{add}}, h^{\max}, h^{\text{LM-Cut}}$) partition the state space into topological structures:
1. **Local Minima**: A state $s$ such that $\forall s' \in \text{succ}(s), \ h(s') \ge h(s)$, but $s \notin S_G$.
2. **Plateaus**: Connected subgraphs of states with identical heuristic values $h(s) = c$.
3. **Exit Distance $ed(s)$**: The minimal length of a path from state $s$ on a plateau to a state $s'$ with strictly lower heuristic value $h(s') < h(s)$.
4. **Dead-Ends**:
   - *Recognized Dead-Ends*: States $s$ where the heuristic correctly identifies insolvability, $h(s) = \infty$.
   - *Unrecognized Dead-Ends (The Fatal Trap)*: States $s$ from which no path to $S_G$ exists ($\text{dist}_{TS}(s, S_G) = \infty$), yet the heuristic estimator is finite: $h(s) < \infty$.

---

## 2. Pathologies: Heuristic Seduction & Branch Divergence

### B. The Mechanism of Heuristic Seduction
Let $\mathcal{M}^* = \langle \mathcal{P}, \mathcal{A}^*, I, G \rangle$ be the ground-truth environment, and let $\hat{\mathcal{M}}$ be a learned or perturbed model where an action $a_{\text{gate}}$ is missing a critical precondition $p_{\text{gate}}$ ($\Delta c > 0$ shortcut-inducing omission):
$$\text{pre}_{\hat{\mathcal{M}}}(a_{\text{gate}}) = \text{pre}_{\mathcal{M}^*}(a_{\text{gate}}) \setminus \{p_{\text{gate}}\}$$

1. **Delete-Relaxation Seduction**: Delete-relaxation heuristics ($h_{\text{FF}}, h^{\text{LM-Cut}}$) compute distances on the relaxed task $\Pi^+$. By omitting $p_{\text{gate}}$, the relaxer does not need to achieve $p_{\text{gate}}$, dropping the estimated cost of reaching $S_G$ via $a_{\text{gate}}$:
   $$\hat{h}(s) = h_{\hat{\mathcal{M}}}(s) \ll h^*(s)$$
2. **Artificial Shortcut Induction**: In $\hat{\mathcal{M}}$, the state graph contains an artificial edge $(s, a_{\text{gate}}, s_{\text{phantom}})$.
3. **$A^*$ Priority Inversion**: Since $f(s) = g(s) + \hat{h}(s)$, the planner greedily prioritizes expanding states along the phantom shortcut over valid physical trajectories.

### C. Theorem: Exponential Branch Divergence $\Omega(b^{D-d})$
When an artificial shortcut leads to an unrecognized dead-end in physical reality:
- Let $D$ be the search depth budget or distance to goal.
- Let $d$ be the depth at which the omitted precondition was bypassed.
- Let $b$ be the effective branching factor in the spurious subtree.

The number of expanded nodes before $A^*$ exhausts the spurious subtree and backtracks to the legitimate branch is lower-bounded by:
$$N_{\text{expanded}} \ge \Omega(b^{D - d})$$
For even modest depth differentials ($D - d \ge 6, b \approx 4$), $N_{\text{expanded}} > 4^6 = 4096$, triggering search timeouts or memory exhaustion.

### D. The Objective Mismatch Theorem
In passive Model-Based RL and Action Model Learning (AML), models are optimized for 1-step prediction accuracy:
$$A_{\text{pred}} = 1 - \frac{1}{|\mathcal{D}|} \sum_{(s, a, s') \in \mathcal{D}} \mathbb{I}(\hat{T}(s, a) \neq s')$$
**The Pathology**: A single omitted bottleneck precondition on an action rarely executed in teacher demonstrations incurs an infinitesimal error $\epsilon \le 0.04$ ($A_{\text{pred}} \ge 96\%$). Yet, during closed-loop heuristic search, an optimizing planner actively seeks out that exact action to minimize plan length, resulting in:
$$\text{PESR} = 0\%$$
High 1-step predictive accuracy does NOT imply play-adequacy or plan execution success.

---

## 3. When to Use This Skill

- When analyzing why an agent or planner fails to find a solution despite high training accuracy.
- When evaluating search-tree metrics: expanded nodes, evaluated nodes, search time, initial $h(s_0)$, and branching factor.
- When diagnosing the difference between **Regime I** ($\Delta c > 0$, shortcut-inducing omissions $\to$ 100% collapse) and **Regime II** ($\Delta c = 0$, cost-preserving / redundant omissions $\to$ preserved solvability).
- When computing Graph Edit Distance (GED) between ground-truth and learned transition graphs.
- When generating state-space visualization, search-tree depth profiles, or heuristic error plots.

## Do Not Use This Skill When
- Parsing raw PDDL syntax or validating typing hierarchies (use `symbolic-world-model-laboratory`).
- Executing multi-fault abduction and online repair loops (use `counterexample-guided-rule-repair`).
- Formulating LaTeX paper submissions (use `scientific-theory-and-paper-architect`).

---

## 4. Rigorous Analytical Workflow

### Step 1: Metric & Solver Harness Setup
- Configure Fast Downward or search engine with exact heuristic configurations:
  - Admissible optimal: `astar(lmcut())`, `astar(blind())`
  - Satisficing: `eager_greedy([ff()])`, `lazy_greedy([ff()])`
- Ensure strict logging of:
  - Search time ($t_{\text{search}}$)
  - Evaluated states ($N_{\text{eval}}$)
  - Expanded states ($N_{\text{exp}}$)
  - Initial heuristic value $h(s_0)$
  - Plan length ($L_{\pi}$) and plan cost ($C_{\pi}$)

### Step 2: Shortcut Potential Quantification ($\Delta c$)
For a given domain modification $\hat{\mathcal{M}}$ relative to $\mathcal{M}^*$:
1. Compute optimal plan cost in ground-truth: $c^* = \text{cost}(\pi^*_{\mathcal{M}^*})$.
2. Compute optimal plan cost in perturbed model: $\hat{c} = \text{cost}(\hat{\pi}_{\hat{\mathcal{M}}})$.
3. Evaluate delta:
   $$\Delta c = c^* - \hat{c}$$
   - If $\Delta c > 0$: **Shortcut-Inducing (Regime I)**. Collapse under $A^*$ is mathematically guaranteed if the shortcut violates physical preconditions.
   - If $\Delta c = 0$: **Cost-Preserving (Regime II)**. Planner does not derive artificial cost advantages; PESR remains positive unless all valid paths are blocked.

### Step 3: Heuristic Error & Seduction Index
Compute the point-wise heuristic distortion across sample states $s \in S$:
$$\epsilon_h(s) = h^*(s) - \hat{h}(s)$$
Identify states where $\epsilon_h(s) \gg 0$ while $s$ is an unrecognized dead-end in physical reality.

### Step 4: Topological Graph Invariants Computation
- **Reachability Ratio**: $\rho_{\text{reach}} = \frac{|S_{\text{reachable}}(\hat{\mathcal{M}})|}{|S_{\text{reachable}}(\mathcal{M}^*)|}$.
- **Graph Edit Distance (GED)**: Minimal number of vertex and edge additions/deletions to transform $TS(\hat{\mathcal{M}})$ into $TS(\mathcal{M}^*)$.

---

## 5. Anti-Hallucination & Mathematical Integrity Protocol

- [ ] **No Guessing of Node Counts**: Never report expanded/evaluated states from intuition. Always parse directly from Fast Downward `stdout` (e.g. `Expanded \d+ state(s)`).
- [ ] **Zero Mocking of Search**: All heuristic values must come from an actual compiled heuristic evaluator (`FastDownwardRunner` or verified search harness).
- [ ] **Distinguish Solvability from Success**: An instance where the planner finds a plan $\hat{\pi}$ has $\text{Solvability} = 100\%$, but if $\hat{\pi}$ fails at step 1 in the real environment, $\text{PESR} = 0\%$. Never conflate plan finding with plan execution validity.
