# Comprehensive Literature Survey: The Local-Global Gap, Action Model Learning, CEGIS, and Decision-Relevant Errors

> **Document Type**: Comprehensive 20-Paper Systematic Survey & Critical Gap Analysis  
> **Target venuse**: Foundations for Master's Thesis & ICAPS / AAAI / AIJ Submissions  
> **Author**: Minh-Phuc Tran  
> **Repository**: `minhphuc477/symbolic-action-model-verification`  
> **Date**: October 2026  

---

## 1. Executive Overview

A central paradox in modern Model-Based Artificial Intelligence—spanning Classical Automated Planning, Model-Based Reinforcement Learning (MBRL), and Program-Synthesized World Models—is the disconnect between **local prediction accuracy** and **global task execution success**. Across domains, models that report near-perfect one-step transition prediction accuracy ($A_{\text{pred}} \ge 98\%$) frequently suffer catastrophic collapse during forward combinatorial search, driving Plan Execution Success Rate ($\text{PESR}$) to $0\%$ and Play Regret ($R_{\text{play}}$) to $\infty$.

This survey systematically reviews **20 landmark papers (2000–2026)** across five foundational pillars:
1. **Local-Global Gap in ML/RL/Planning**: The mathematical and conceptual divergence between passive one-step loss minimization and downstream closed-loop control.
2. **Action Model Learning (AML)**: State-of-the-art symbolic schema acquisition from observation traces (FAMA, LOCM2, FastLAS, SAM, lifted STRIPS).
3. **CEGIS & Program Repair**: Counterexample-Guided Inductive Synthesis and abstraction refinement architectures.
4. **Spurious Paths & Phantom Edges**: Combinatorial search-graph overapproximations and topological shortcuts.
5. **Decision-Relevant Error & Rule Interventions**: Frameworks isolating how sparse rule modifications break passive learners.

---

## 2. Master Comparison Table (20 Landmark Papers)

| # | Paper & Authors | Thematic Pillar | Identified Research Gap | Core Method / Framework | Author-Confessed Limitations & Blindspots |
|:---:|:---|:---|:---|:---|:---|
| **1** | **Lambert et al. (CoRL 2020)**<br>*Objective Mismatch in Model-Based RL* | Local-Global Gap | Maximizing one-step MLE transition likelihood does not correlate with or guarantee downstream policy return. | Analyzes mismatch in continuous control; benchmarks deep dynamics models (PETS, MBPO) on MuJoCo. | Confined strictly to continuous spaces; offers empirical heuristic fixes (ensembles, reward tuning) without formal causal guarantees for combinatorial discrete domains. |
| **2** | **Voelcker et al. (NeurIPS 2022)**<br>*Value Equivalence in Model-Based RL* | Local-Global Gap | Standard dynamics models model all transitions uniformly, wasting capacity on task-irrelevant dynamics. | Formulates Value-Equivalent World Models via bellman operator projections. | Requires prior knowledge of value function family; intractable exact computation in discrete factored combinatorial state spaces. |
| **3** | **Yu et al. (arXiv 2026 / L430)**<br>*How Should World Models Be Evaluated?* | Local-Global Gap | Massive metric diversity and claim/evidence mismatch: video quality or prediction accuracy does not establish decision-making adequacy. | Position paper categorizing world model usages into 5 tiers; proposes decision-centric evaluation protocols. | High-level taxonomical survey; does not provide a constructive repair algorithm or sample complexity proofs for discrete symbolic systems. |
| **4** | **Ha & Schmidhuber (NeurIPS 2018)**<br>*Recurrent World Models Facilitate Policy Evolution* | Local-Global Gap | Latent world models suffer from "adversarial exploitation" where policy agents exploit model hallucinations to get infinite virtual reward. | VAE + MDN-RNN latent world simulator coupled with CMA-ES controller. | Requires artificial temperature hacks / penalties to prevent the controller from exploiting ungrounded latent shortcuts. |
| **5** | **Aineto et al. (AIJ 2019)**<br>*Learning Action Models with Minimal Observability (FAMA)* | Action Model Learning | Existing learners require full state observability or fail when intermediate states in trajectories are unobserved. | Compiles action model learning into a classical planning problem solved via Fast Downward / SAT. | Strictly passive; computational complexity scales exponentially with missing state tokens; cannot interact actively to test unobserved preconditions. |
| **6** | **Cresswell et al. (AIJ 2013)**<br>*Acquiring Generalised Domain Models (LOCM2)* | Action Model Learning | Inability to extract multiple concurrent state machines for objects from pure action sequences without state annotations. | Induces parameterized Finite State Machines (FSMs) by analyzing contiguous action transitions and object bindings. | Assumes noise-free sequential traces; strictly passive; incapable of learning non-relational or global bottleneck preconditions. |
| **7** | **Law et al. (AAAI 2020)**<br>*FastLAS: Scalable ILP for Answer Set Programming* | Action Model Learning | Standard ILP systems scale poorly when learning non-monotonic rules with large hypothesis spaces. | Computes custom language bias constraints and solves task-independent optimization over ASP answer sets. | Requires pre-defined meta-language bias schemas; passive batch learning; cannot handle online plan-prefix failures. |
| **8** | **Gösgens et al. (ICAPS 2025)**<br>*Learning Lifted STRIPS Models from Traces Alone* | Action Model Learning | Learning lifted relational schemas without prior knowledge of predicate inventories or arities is computationally prohibitive. | Maps trace sequences into a minimal lifted transition graph using SAT-based relational matching. | Purely passive batch induction; requires rich traces; completely vulnerable to search-tree collapse if traces lack negative bottleneck examples. |
| **9** | **Solar-Lezama (PhD Thesis / CACM 2008)**<br>*Program Synthesis by Sketching (CEGIS)* | CEGIS & Repair | Combinatorial program spaces are too vast for brute-force verification or unguided search. | Counterexample-Guided Inductive Synthesis (CEGIS): Inductive Synthesizer couples with SMT Verifier in a feedback loop. | Assumes an exact formal specification or complete oracle exists; originally designed for boolean circuits/syntax, not reachability-constrained planning trees. |
| **10** | **Clarke et al. (CAV 2000)**<br>*Counterexample-Guided Abstraction Refinement (CEGAR)* | CEGIS & Repair | State explosion in model checking makes verifying industrial circuits and software intractable. | Iteratively refines abstract state transitions by eliminating spurious counterexamples via SAT/SMT checks. | Designed for verification of static finite-state hardware, not online learning of physical environment dynamics under active planning. |
| **11** | **Seipp & Helmert (AIJ 2018)**<br>*CEGAR for Classical Planning* | CEGIS & Repair | Cartesian abstractions for optimal planning heuristics are either too coarse or too large to compute. | Adapts CEGAR to compute additive abstraction heuristics ($h^{\text{CEGAR}}$) for $A^*$ search in Fast Downward. | Focuses purely on heuristic generation for fixed ground-truth models; does not address learning or repairing the underlying PDDL domain itself. |
| **12** | **Grand et al. (ICML 2025)**<br>*WorldCoder: Program Synthesis for World Models* | CEGIS & Repair | Neural world models are opaque and struggle with exact combinatorial logic in interactive environments. | Uses LLM code synthesis with a CEGIS-like verifier to synthesize executable Python world models. | Relies on LLM code generation heuristics; prone to timeout; lacks formal query complexity bounds under reachability constraints. |
| **13** | **Fan & Holte (AAAI 2021)**<br>*Spurious Paths in State Space Abstractions* | Spurious Paths | Abstract search heuristics often select paths that do not correspond to any valid concrete trajectory (spurious shortcuts). | Formalizes spurious path conditions in abstract state spaces and measures search overhead. | Analyzes abstract heuristics rather than learned action models; does not study the causal decoupling with passive accuracy. |
| **14** | **Amir & Chang (JAIR 2008)**<br>*Learning Partially Observable Deterministic Models (SLAF)* | Spurious Paths | Online model learning under partial observability often admits exponential spurious transition hypotheses. | Simultaneous Learning and Filtering (SLAF): Maintains exact belief-state formulas using DNF/CNF logical filtering. | Exact logical representation grows exponentially with horizon $t$; requires hand-crafted initial logical bounds. |
| **15** | **Yang et al. (IJCAI 2007)**<br>*Learning Action Models from Plan Traces (ARMS)* | Spurious Paths | Acquiring PDDL schemas from noisy or incomplete traces without intermediate states leads to unsound action models. | Formulates action model induction as a Weighted Max-SAT problem over frequent pattern constraints. | Produces approximate models that frequently omit rare preconditions, directly inducing phantom search-tree shortcuts. |
| **16** | **Helmert (JAIR 2006)**<br>*The Fast Downward Planning System* | Spurious Paths | Forward search in classical planning suffers from exponential branching factor without causal decomposition. | Translates PDDL to multi-valued planning tasks (SAS+), builds causal graphs, and searches with admissible heuristics ($h^{\text{LM-cut}}$). | A cost-minimizing planner inherently acts as an adversarial tester against incomplete models, deterministically exploiting phantom edges. |
| **17** | **Martín (arXiv 2026 / L446)**<br>*When a Verified World Model Still Loses* | Decision-Relevant Error | Sampling-based verification gates (100% transition accuracy) are blind to rare pivotal dynamics that cause 100% loss at play. | Formalizes the law $\text{danger} = \text{play\_cost} \cdot (1 - \text{rarity})^N$; evaluates LLM CWMs on game distributions. | Diagnostic critique of LLMs; lacks a constructive active repair algorithm and does not provide formal search-tree topology theorems. |
| **18** | **Gao et al. (arXiv 2026 / L447)**<br>*MirrorCraft: Paired Evaluation under Rule Changes* | Decision-Relevant Error | Existing AI agent benchmarks evaluate on static mechanics, obscuring whether agents can adapt when rules change. | Paired benchmark in Minecraft (Vanilla vs Mirror worlds) under server-side datapack rule interventions. | Coarse bundled evaluation suites; does not isolate planning search burden from model-learning sample complexity. |
| **19** | **Aineto & Scala (AAAI 2024)**<br>*Action Model Learning with Guarantees (VSLAM)* | Decision-Relevant Error | Action model learners lack formal convergence guarantees and cannot distinguish between sound and complete approximations. | Version Space Learning for Action Models (VSLAM): Tracks lower bound $LH$ (sound) and upper bound $UH$ (complete). | Purely passive batch stream; requires explicit negative demonstrations; fails when data contains only positive successful play traces. |
| **20** | **Annual Reviews in Control (2026 / L443)**<br>*Control-Oriented System Identification* | Decision-Relevant Error | Classical system identification minimizes output prediction error rather than preserving control-relevant system dynamics. | Survey of classical, learning, and physics-informed identification for downstream control guarantees. | Confined to continuous dynamical systems (ODEs/PDEs); does not address discrete relational STRIPS action models or search trees. |

---

## 3. Thematic In-Depth Synthesis & Critical Analysis

### 3.1 Pillar 1: The Local-Global Objective Mismatch
The disconnect between local prediction error and global task performance was first rigorously formalized in continuous control by **Lambert et al. (2020)**. They proved that minimizing mean squared error (MSE) over one-step transitions $\min_\theta \mathbb{E}[\|s_{t+1} - f_\theta(s_t, a_t)\|^2]$ does not align with maximizing expected return $J(\pi) = \mathbb{E}[\sum r(s_t, a_t)]$. When an optimizer (policy gradient or trajectory planner) searches through model predictions, it aggressively exploits local inaccuracies where the model erroneously overestimates reward or accessibility. **Voelcker et al. (2022)** attempted to remedy this via *value equivalence*, arguing that models only need to be accurate with respect to the Bellman operator over a restricted policy family. Concurrently, **Yu et al. (2026)** underscored that this "claim/evidence mismatch" is now rampant in world model benchmarks: generative video quality or transition accuracy fails to predict closed-loop task execution.

*Critical Assessment*: While continuous MBRL has identified this failure mode, its solutions (pessimistic value bounds, ensembles) are heuristic and cannot provide exact guarantees in discrete combinatorial settings where an omitted boolean condition causes binary failure.

### 3.2 Pillar 2: Passive Action Model Learning and Its Blindspots
Symbolic Action Model Learning has progressed from early SAT formulations (**ARMS; Yang et al., 2007**) and exact logical filtering (**SLAF; Amir & Chang, 2008**) to classical planning compilation (**FAMA; Aineto et al., 2019**), state machine induction (**LOCM2; Cresswell et al., 2013**), and Answer Set Programming (**FastLAS; Law et al., 2020**). Most recently, **Gösgens et al. (ICAPS 2025)** presented a scalable method to learn lifted STRIPS models from raw action traces without predicate inventories.

*Critical Assessment*: Across all these works, learning is strictly **passive**: the algorithm is provided a dataset of execution traces $\mathcal{D}$ and searches for a model $\widehat{M}$ that is syntactically consistent with $\mathcal{D}$. When training traces represent successful expert play, they do not traverse states where critical preconditions fail. As a result, passive learners systematically learn *overly permissive* action models (missing preconditions).

### 3.3 Pillar 3: Counterexample-Guided Synthesis (CEGIS & CEGAR)
The foundational principle of refining models via counterexamples traces back to **Clarke et al. (2000)** (CEGAR) in hardware verification and **Solar-Lezama (2008)** (CEGIS) in program synthesis. In classical planning, **Seipp & Helmert (2018)** applied CEGAR to compute abstraction heuristics by iteratively splitting abstract states that admit spurious plans. In the modern generative era, **Grand et al. (2025)** (WorldCoder) demonstrated that CEGIS can guide LLMs to write game simulators by testing code rollouts against an environment oracle.

*Critical Assessment*: CEGAR in planning has historically been used to build *admissible heuristics* for a known, fixed PDDL domain, rather than repairing an unknown or mutated domain. WorldCoder, while innovative, relies on stochastic LLM code synthesis without sample complexity bounds. A formal, polynomial-time counterexample-guided repair engine for relational PDDL under reachability constraints has remained an open void.

### 3.4 Pillar 4: Spurious Paths and Combinatorial Search Overapproximation
When an action model is overly permissive, what happens inside the planner? **Fan & Holte (AAAI 2021)** studied spurious paths in abstract state spaces, demonstrating that spurious edges severely degrade heuristic search efficiency. In our context, an incomplete action schema does not just slow down search—it creates **phantom paths** to the goal. Because cost-minimizing forward planners like **Fast Downward (Helmert, 2006)** use admissible heuristics ($h^{\text{LM-cut}}$), they are mathematically designed to find the shortest path. If an omitted precondition creates an unconstrained shortcut, the planner is mathematically guaranteed to select it.

### 3.5 Pillar 5: Decision-Relevant Errors and Sparse Rule Interventions
The paper closest to our problem formulation is **Martín (arXiv:2607.14169, July 2026 / L446)**. Martín demonstrated that LLM-synthesized code world models can achieve $100\%$ transition accuracy on sample trajectories yet suffer $100\%$ loss when deployed in actual play. The error lies in rare "pivotal rules" that govern terminal conditions or bottlenecks. Concurrently, **MirrorCraft (Gao et al., 2026 / L447)** demonstrated that LLM agents in Minecraft collapse when server-side datapacks alter game recipes. **Aineto & Scala (AAAI 2024)** introduced VSLAM, formalizing sound and complete action models via version spaces, but acknowledged that recovering missing constraints passively requires exhaustive negative traces.

*Critical Assessment*: Martín's work is a diagnostic exposé of LLMs, not an algorithmic solution. MirrorCraft bundles rule mutations into broad suites, preventing mathematical isolation. Our thesis provides the missing theoretical foundation: formalizing the exact topological divergence of search trees under sparse mutations and proving a polynomial-time active repair bound.

---

## 4. Synthesis: The Unoccupied Research Space

The intersection of these 20 landmark papers reveals an unoccupied, high-impact scientific niche:

```text
    Continuous Control / MBRL                Passive Symbolic AML
   [Lambert 2020, Voelcker 2022]            [FAMA 2019, LOCM2 2013, ICAPS 2025]
        \                                            /
         \                                          /
          ▼                                        ▼
   Objective Mismatch Exists             Overly Permissive Models Learned
   (Heuristic Ensembles, no logic)       (Passive traces miss bottleneck rules)
                  \                      /
                   \                    /
                    ▼                  ▼
              =============================================
              THE OPEN SCIENTIFIC VOID (THIS THESIS):
              1. Formal Theorem of Search-Tree Topology Collapse
                 (d_triangle = Omega(b^(D-d)) while A_pred >= 1 - eps)
              2. Active Closed-Loop Repair (CEG-OMR)
                 (Planner Generator -> Oracle Verifier -> Horn Synthesizer)
              3. Provable Polynomial Query Complexity Bound
                 (K_repair <= k · diam(G_T) · |F|^r)
              =============================================
                    /                  \
                   /                    \
                  ▼                      ▼
        Model Checking / CEGIS            Empirical Diagnostic Gap
         [Clarke 2000, Seipp 2018]        [Martín 2026, MirrorCraft 2026]
         (Static verification, not AML)   (Diagnostic critique, no repair algorithm)
```

By bridging these five distinct literatures, our research transforms what was previously perceived as a narrow empirical curiosity into a fundamental theorem of model-based reasoning.
