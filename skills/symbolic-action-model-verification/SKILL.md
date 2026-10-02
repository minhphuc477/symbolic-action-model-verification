---
name: symbolic-action-model-verification
description: Specialized research engineering skill for benchmarking search-tree topology collapse, the verified-vs-correct gap, and Counterexample-Guided Online Model Repair (CEG-OMR) under rule interventions.
metadata:
  model: inherit
---

# Symbolic Action Model Verification & Online Repair Skill

## Purpose
Specialized AI research engineering skill for executing severe-testing verification, benchmarking search-tree topology collapse, and running Counterexample-Guided Online Model Repair (CEG-OMR) across native symbolic learners (LOCM2, FAMA, FastLAS) and heuristic planners (Fast Downward).

> [!NOTE]
> This skill operates in tandem with [`ceg-omr-repair`](../ceg-omr-repair/SKILL.md) to benchmark online counterexample-guided repair against static offline learners.

## Core Verification Rules (`RESEARCH_RULES.md`)
1. **Zero Synthetic Metric Approximations**: All metrics ($A_{\text{pred}}$, $d_\Delta$, $\text{PESR}$, $R_{\text{play}}$, $K_{\text{repair}}$) must derive from real $A^*$ search or Fast Downward plan rollouts on native solvers.
2. **Distinct Algorithmic Precondition Profiles**:
   - **LOCM2**: FSM object-centric learner. Omits non-object state fluents under bottleneck interventions.
   - **ARMS**: Association rule miner. Omits multi-argument preconditions and static constraints.
   - **SLAF**: SAT-based trace filter. Omits state bounds under sparse trace samples.
   - **FAMA**: SAT/HTN compilations (`meta_planning`). Over-generalizes under partial state traces.
   - **FastLAS**: Inductive logic programming (`clingo`). Induces exact Horn clause rules when complete mode bias is provided.
   - **CEG-OMR**: Active online repair using counterexample queries from execution failures to tighten Horn preconditions in polynomial steps.
3. **Strict Logical Consistency**:
   - If $d_\Delta = 0.00$ (exact transition model), $\text{PESR} = 1.0$ ($100\%$) and $R_{\text{play}} = 0$.
   - If $d_\Delta > 0$ (phantom edges exist), execution on ground-truth $M^*$ fails at the phantom transition step ($\text{PESR} = 0.0$, $R_{\text{play}} = \infty$) unless repaired via CEG-OMR.

## Workflow Steps
1. Prepare ground-truth and mutant PDDL domains via `src/interventions/pddl_mutator.py`.
2. Execute learner algorithms (LOCM2, FAMA, FastLAS) or inject controlled rule interventions.
3. Evaluate plan execution via Fast Downward across ground-truth $M^*$ and learned/mutated $\widehat{M}$.
4. If execution fails, activate CEG-OMR repair loop in `src/repair/ceg_omr_engine.py` to synthesize tightened preconditions from counterexamples.
5. Compute non-parametric statistics via `src/metrics/statistical_rigor.py` (Wilcoxon signed-rank, Holm-Bonferroni, Cohen's d, 95% Bootstrap CIs).
