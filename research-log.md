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
