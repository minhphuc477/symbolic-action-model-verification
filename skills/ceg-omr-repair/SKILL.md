---
name: ceg-omr-repair
description: Specialized AI research and engineering skill for executing Counterexample-Guided Online Model Repair (CEG-OMR) under PDDL rule interventions across Sokoban, Blocksworld, Gridworld, and Logistics with native Fast Downward, FastLAS, and non-parametric statistical rigor.
metadata:
  model: inherit
---

# Counterexample-Guided Online Model Repair (CEG-OMR) Skill

## 1. Overview & Research Objective
This skill provides end-to-end guidance and automated execution protocols for the MSc Thesis / Flagship Paper:
**"Counterexample-Guided Repair of Action Models under Rule Interventions"**

### Theoretical Motivation
Offline action model learners (LOCM2, FAMA, ARMS, SLAF) and deep world models often report high passive transition prediction accuracy ($A_{\text{pred}} \approx 1.0$), yet experience catastrophic failure during actual planning execution ($R_{\text{play}} = \infty$, PESR $= 0.0$). This occurs because missing preconditions introduce **phantom transitions** in the search fringe that heuristic planners ($A^*$, Fast Downward) exploit as shortcuts.

**CEG-OMR** resolves this through an active verification loop:
1. **Generator (Planner)**: Computes candidate plan $\pi = \langle a_0, \dots, a_{T-1} \rangle$ on candidate model $\widehat{M}$ using Fast Downward.
2. **Oracle Verifier (Game Engine / Environment)**: Executes actions step-by-step on true world $M^*$. If action $a_t$ fails at state $s_t$, it emits a concrete counterexample $\kappa = (s_t, a_t, \bot)$.
3. **Synthesizer (Model Repair)**: Identifies violated fluents and tightens preconditions via Horn clause elimination:
   $$\text{pre}(a) \leftarrow \text{pre}(a) \cup \{ f \in \mathcal{F} \mid s_t \not\models f \}$$
   Provably eliminating the invalid transition without removing valid transitions (Lemma 1 & Lemma 2).

---

## 2. Strict Methodological Rules (`RESEARCH_RULES.md`)
1. **Zero Synthetic/Mock Data**: Every number, table entry, and plot must originate from deterministic solver execution logs (`wsl_ubuntu` Fast Downward, FastLAS, FAMA). Never use `np.random` or synthetic approximations.
2. **Full Environmental Fidelity**: Planning must execute with native PDDL solvers in Linux (`venv_linux` under WSL Ubuntu).
3. **Multi-Seed Statistical Rigor**: Minimum 30 problem instances $\times$ 5 seeds = 150 runs per condition. All comparisons require Wilcoxon signed-rank tests with Holm-Bonferroni correction and 95% bootstrap confidence intervals.

---

## 3. Intervention Typology (PDDL Mutations)
When mutating domain models to evaluate repair capabilities, apply three standard intervention classes:

| Class | Mutation Operator | Impact on Transition Graph | Failure Mode |
|---|---|---|---|
| **Type I** | Precondition Drop ($\text{pre}(a) \setminus \{p\}$) | Adds phantom edges: $E(M^*) \subset E(\widehat{M})$ | Agent hallucinates valid moves; execution fails at runtime |
| **Type II** | Extraneous Precondition ($\text{pre}(a) \cup \{q\}$) | Removes valid edges: $E(\widehat{M}) \subset E(M^*)$ | Over-constrained model; planner declares solvable tasks unsolvable |
| **Type III** | Inverted Effect ($\text{eff}^+(a) \setminus \{e\}$) | Distorts state transitions | Plan reaches unintended states, diverging from goal trajectory |

---

## 4. Execution Workflow

### Step 1: Environment Preflight
Ensure the WSL Ubuntu environment and solvers are reachable:
```bash
wsl -d Ubuntu -e bash -c "source /mnt/f/Thesis/venv_linux/bin/activate && python3 -c 'import pddl; print(\"PDDL parser OK\")'"
```

### Step 2: Generate Controlled Interventions
Mutate ground-truth domain models using `src/interventions/pddl_mutator.py`:
```bash
python src/interventions/pddl_mutator.py \
  --domain domains/sokoban/domain.pddl \
  --type drop_precondition \
  --action move \
  --predicate clear \
  --output domains/sokoban/mutants/type1_drop_clear.pddl
```

### Step 3: Run CEG-OMR Repair Loop
Execute the repair harness against the mutant domain:
```bash
wsl -d Ubuntu -e bash -c "source /mnt/f/Thesis/venv_linux/bin/activate && python3 src/repair/ceg_omr_engine.py \
  --domain domains/sokoban/mutants/type1_drop_clear.pddl \
  --oracle-domain domains/sokoban/domain.pddl \
  --problems domains/sokoban/problems/ \
  --planner fast_downward \
  --max-iterations 20 \
  --output benchmark_outputs/ceg_omr_sokoban_run.json"
```

### Step 4: Run Baseline Comparisons
Benchmark CEG-OMR against baselines:
- **SAM** (Stern & Juba IJCAI 2017; Juba et al. KR 2021)
- **FAMA** (Aineto, Celorrio, Onaindia AIJ 2020)
- **Random Probing** (Kearns & Singh 2002)
- **Naive Replanning** (Fox et al. ICAPS 2006)

### Step 5: Statistical Rigor & Reporting
Compute non-parametric metrics and generate publication-ready tables:
```bash
python src/metrics/statistical_rigor.py \
  --results benchmark_outputs/ceg_omr_sokoban_run.json \
  --alpha 0.01 \
  --output figures/table1_repair_benchmarks.tex
```

---

## 5. Verification Checklist for Papers
- [ ] Lemma 1 verified: $\widehat{M}$ never eliminates true transitions during precondition tightening.
- [ ] Lemma 2 verified: Repair convergence $K_{\text{repair}} \le k |\mathcal{F}|^r$ holds empirically with tightness ratio $\rho \le 1.0$.
- [ ] Test sets clearly separated into Passive Traces ($D_{\text{passive}}$) vs Active Search Fringe ($D_{\text{fringe}}$).
- [ ] All native solver logs archived with cryptographic hashes (SHA-256) in `benchmark_outputs/`.
