---
name: symbolic-action-model-verification
description: Specialized research engineering skill for benchmarking search-tree topology collapse and the verified-vs-correct gap in lightweight symbolic action model learning under rule interventions.
metadata:
  model: inherit
---

# Symbolic Action Model Verification & Search-Tree Topology Collapse Skill

## Purpose
Specialized AI research engineering skill for running severe-testing verification and benchmarking search-tree topology collapse in symbolic action model learning (LOCM2, FAMA, FastLAS, ARMS, SLAF).

## Core Verification Rules
1. **Zero Synthetic Metric Approximations**: All metrics ($A_{\text{pred}}$, $d_\Delta$, $\text{PESR}$, $R_{\text{play}}$) must derive from real $A^*$ grid state-space rollouts or verified algorithms.
2. **Distinct Algorithmic Precondition Profiles**:
   - **LOCM2**: FSM object-centric learner. Omits non-object state fluents under bottleneck interventions.
   - **ARMS**: Association rule miner. Omits multi-argument preconditions and static constraints.
   - **SLAF**: SAT-based trace filter. Omits state bounds under sparse trace samples.
   - **FAMA**: SAT/HTN compilations (`meta_planning`). Over-generalizes under partial state traces.
   - **FastLAS**: Inductive logic programming (`clingo`). Induces exact horn clause rules when complete mode bias is provided.
3. **Strict Logical Consistency**:
   - If $d_\Delta = 0.00$ (exact transition model), $\text{PESR} = 1.0$ ($100\%$) and $R_{\text{play}} = 0$.
   - If $d_\Delta > 0$ (phantom edges exist), execution on ground-truth $M^*$ fails at the phantom transition step ($\text{PESR} = 0.0$, $R_{\text{play}} = \infty$).

## Workflow Steps
1. Parse 2D Grid states and execution traces via `PuzzleScriptAdapter`.
2. Execute learner algorithms (LOCM2, FAMA, FastLAS) to obtain domain models.
3. Evaluate plan execution via `RealAStarPlanner` across ground-truth $M^*$ and learned $M_{\text{learned}}$.
4. Calculate non-parametric statistics via `StatisticalRigorEngine` (Wilcoxon signed-rank, Benjamini-Hochberg FDR, Cohen's d, 95% Bootstrap CIs).
5. Plot publication-quality figures via `BenchmarkPlotter`.
