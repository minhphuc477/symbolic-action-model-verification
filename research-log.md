# Research Decision Log

## Initial Bootstrap & Setup
- **Date**: 2026-09-26
- **Action**: Initialized Scientific Autoresearch framework (Two-Loop Architecture).
- **Decision Owner**: MSc Candidate & AI Research Agent
- **Key Baseline Decisions**:
  1. Audited 412 literature entries from `ai_games_research_ledger_2026-09-09_v50_external_runtime_harness.xlsx`.
  2. Selected `L446` (ICLR 2026 - Code World Models) and `L447` (MirrorCraft 2026) as primary empirical counter-anchors.
  3. Identified core problem: **Verified-vs-Correct Gap** (Transition Prediction Accuracy != Planning Adequacy).
  4. Locked 18-month 2-paper roadmap:
     - **Paper 1 (Month 7)**: Diagnostic Benchmark (IEEE Transactions on Games / ACM FDG).
     - **Paper 2 (Month 15)**: Causal-Fidelity World Models (ICLR / NeurIPS / AAAI / AIJ).

## Entry 001 - Literature & Gap Verification Lock
- Verified non-predatory status of core references (purged MDPI references L426 and updated L204 to Minato 1993 ZDD).
- Formulated primary estimands: Play Regret ($R_{\text{play}}$) and Rule Intervention Effect ($\text{RIE}$).

## Entry 002 - Non-Human Study Lock & 2025-2026 Literature Grounding
- **Date**: 2026-09-26
- **Key Decisions**:
  1. Locked 100% computational & algorithmic methodology with **ZERO human subject studies** (IRB-free, fully automated baseline verification).
  2. Mapped Connected Papers citation networks across 4 lineages (World Models, Action Models, PCG-QD, GGP/Rule Interventions).
  3. Grounded 5 critical research blindspots in 2025-2026 literature (WorldCoder, CUBE, MCP-Universe, World-Time Compute, Grounding Before Generalizing, PAC-MDP Bounds).
  4. Locked Paper 1 (IEEE ToG / ACM FDG) RQs on diagnostic capacity, burden decoupling, and world-time compute Pareto frontiers.
  5. Locked Paper 2 (ICLR / NeurIPS / AIJ) RQs on Active Counterexample-Guided Tree Synthesis (ACE-Tree) and $O(k)$ Sparse PAC Bounds.

## Entry 003 - Track Lock: Combined Option A (World Models) + Option B (PCG-QD)
- **Date**: 2026-09-26
- **Key Decision**:
  - Combined **Option A (World Models & Active Tree Probing)** and **Option B (Procedural Content Generation & Quality-Diversity)** into a unified, synergistic 1.5-year 2-Paper program:
    - **PCG-QD (CMA-ME)** acts as the automated adversarial game & rule intervention generator.
    - **Active Tree Probing** acts as the verification engine for Code World Models.
  - **Paper 1 Target (Month 7)**: *PCG-QD Interventional Benchmark: Automated Quality-Diversity Synthesis of Rule Perturbations for Code World Model Verification* (IEEE ToG / ACM FDG).
  - **Paper 2 Target (Month 15)**: *Co-Evolutionary World Model Probing: Zero-Shot Causal Adaptation via Active Counterexample-Guided Tree Synthesis on QD Archives* (ICLR / NeurIPS / AIJ).

## Entry 007 - Unbiased Multi-Domain Research Program Lock
- **Date**: 2026-09-26
- **Key Actions & Decisions**:
  1. **Purged Single-Engine Tunnel Vision**: Removed exclusive bias toward PuzzleScript/Sokoban grid toys. Expanded research problem to universal domain-agnostic Code World Model verification and adaptation.
  2. **Multi-Domain Synthesis**: Authored `UNBIASED_MULTI_DOMAIN_GAME_AI_RESEARCH_PROGRAM.md` mapping 7 Game AI subfields and 3 evaluation domains (Grid DSL, Minecraft JSON datapacks in MirrorCraft, SWE-bench AST code repos).
  3. **Universal Algorithmic Architecture**: Formulated Theorem 1 PAC Bounds ($O(k \log(1/\delta))$) and ACE-Tree Zero-Shot AST Code Patching as domain-agnostic algorithms applicable across text, code, voxel, and grid game agents.

## Entry 008 - Codebase Cleanup, Proposition 1 6-Gap Refinement & Theoretical Grounding
- **Date**: 2026-09-26
- **Key Actions & Decisions**:
  1. **Paper Titles Locked**:
     - **Paper 1 Title**: *"Benchmarking Search-Tree Topology Collapse in Lightweight Symbolic Action Models under Rule Interventions"* (IEEE Transactions on Games / ACM FDG).
     - **Paper 2 Title**: *"Goal-Directed Counterexample-Guided Active Synthesis for Repairing Symbolic World Models under Sparse Rule Modifications"* (AIJ / AAAI / ICAPS / ICLR).
  2. **Codebase Cleaned & Purged of Fake Data**:
     - Deleted all fake data scripts (`counterexample_100_states_verification.py`, `compute_empirical_table.py`, `generate_final_slr_master_artifact.py`, 23 root clutter scripts).
     - Cleaned `src/runners/real_external_runner.py`: Fixed SLAF runner description (Symbolic Learning via Action Filtering, Amir & Chang 2008), removed dummy hardcoded return strings, and enforced `RealExecutionError` if native binaries are missing.
  3. **Proposition 1 (Search-Tree Phantom Path Divergence) 6-Gap Fixes**:
     - Stated and proved *Lemma 1 (No-Edges-Lost)*: $E_T \subseteq \hat{E}_T \implies |E_T \setminus \hat{E}_T| = 0$.
     - Explicitly formalized *Uniform-Depth Cut Assumption*, *Fresh-Subtree Assumption*, and *Test Set Definition* $\mathcal{D}_{\text{test}} = E_T \cup (\hat{E}_T \setminus E_T)$.
     - Derived exact exponential lower bound $d_\triangle(G_T, \hat{G}_T) = \Omega(b^{D-d})$ for $b \ge 2$, and $A_{\text{pred}}(\hat{M}) \ge 1 - b^{-d}$.
     - Corrected 2-part counterexample arithmetic (Linear Chain $b=1$ vs Binary Tree $b=2$).
  4. **Purged SCM & Mathiness**:
     - Completely removed circular SCM $d$-separation claims and tautological upper bounds.
  5. **Integrated 2020-2026 Mathematical Literature**:
     - Paper 1 theoretical foundation: Proposition 1 + Distance Sensitivity Oracles (DSO) + Causal Bisimulation Metric (Beckers & Halpern / Ferns et al.).
     - Paper 2 theoretical foundation: Angluin $L^*$ Horn Clause Learning & RTD Bounds ($K_{\text{CEGIS}} \le \mathcal{O}(k \cdot d \cdot \log n)$) + Galois Connections.

## Entry 009 - Advanced 4-Pillar Mathematical Synthesis (TDA, MDL, OT, Coalgebras)
- **Date**: 2026-09-26
- **Key Actions & Decisions**:
  1. **Integrated 4 Advanced Mathematical Frontiers**:
     - **Pillar 1: Topological Data Analysis (TDA)**: Proved Theorem 1.1 (Phantom Cycle Detection via $\beta_1 > 0$ persistence intervals) and Theorem 1.2 (Persistence Diagram Bottleneck Distance $\mathcal{W}_\infty$ bound under edge perturbations).
     - **Pillar 2: Information Theory & MDL**: Proved Theorem 2.1 (Minimum Observation Trace Complexity $T \ge \frac{K(\mathcal{M}^*) - \log(1/\delta)}{I - R(\epsilon)}$) and Theorem 2.2 (PAC-MDL Precondition Generalization Error Bound).
     - **Pillar 3: Optimal Transport & Wasserstein Metrics**: Proved Theorem 3.1 (Cumulative Tree Search Error Accumulation $W_1(\mu_d, \hat{\mu}_d) \le \epsilon_{local} \frac{L_{max}^d - 1}{L_{max} - 1}$) and Theorem 3.2 (MCTS Value Suboptimality under Precondition Perturbation).
     - **Pillar 4: Category Theory & Coalgebras**: Proved Theorem 4.1 ($T$-Coalgebra Homomorphism Soundness for Abstract World Models $T(X) = (O \times X)^A$) and Theorem 4.2 (Zero-Shot Monadic Rule Transfer Bound in Kleisli Category $\mathcal{K}l(M)$).
  2. **Unified Theoretical Architecture**:
     - **Paper 1 Enhancement**: Combined TDA ($\beta_1$ persistence) with Two-Part MDL to create a topologically regularized MDL loss function $\mathcal{L}_{TDA-MDL}(\mathcal{M}, \mathcal{D}_T) = L(\mathcal{M}) + L(\mathcal{D}_T \mid \mathcal{M}) + \lambda \cdot \mathcal{W}_\infty(\mathcal{D}_1, \emptyset)$.
     - **Paper 2 Enhancement**: Combined Wasserstein OT error bounds with Coalgebraic Bisimulation to trigger active CEGIS queries dynamically whenever $W_1$ tree divergence exceeds bisimulation metric radius.
