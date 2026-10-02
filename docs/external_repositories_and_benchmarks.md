# Canonical External Repositories, Benchmarks, and Baseline Ecosystem

**Document Version:** 1.0.0  
**Date:** 02/10/2026  
**Scope:** Action Model Learning (AML), CEGIS Model Repair, and Classical Planning Benchmark Suites  
**Author:** Le Tran Minh Phuc (Master's Thesis in AI/Computer Science)

---

## 1. Executive Summary

This monograph systematically catalogs the canonical academic open-source repositories and standard benchmark ecosystems for Action Model Learning (AML), Safe Action Model Learning (SAM), Inductive Logic Programming (ILP), and classical International Planning Competition (IPC) domains.

Every repository listed below has been verified via live web research and source-code inspection. These tools constitute the authoritative empirical baseline landscape against which **CEG-OMR (Counterexample-Guided Online Model Repair)** is evaluated.

---

## 2. Canonical Action Model Learning & Repair Repositories

### 2.1. FAMA (Fast Action Model Acquisition / Classical Planning Compilation)

- **Original ICAPS 2018 Repository:**  
  [`https://github.com/sjimenezgithub/strips-learning`](https://github.com/sjimenezgithub/strips-learning)  
  *Authors:* Diego Aineto, Sergio Jiménez, Eva Onaindia  
  *Paper:* "Learning STRIPS Action Models with Classical Planning" (ICAPS 2018; AIJ 2019)  
  *Core Files:*  
  - `compiler.py`: Compiles action model learning from partial traces into a classical planning problem.
  - `evaluator2.py`: Compares learned domain against ground-truth domain on test problem instances.
  - `benchmarks/icaps18/`: Contains blocksworld, gripper, and driverlog instances.

- **Generalized Meta-Planning Toolkit:**  
  [`https://github.com/daineto/meta-planning`](https://github.com/daineto/meta-planning)  
  *Author:* Diego Aineto  
  *Structure:* Modular Python library (`pip install -e .`) providing:
  - `src/meta_planning/generator/`: Plan generation and trace sampling.
  - `src/meta_planning/observations/`: Observation noise, partial observability filters.
  - `src/meta_planning/parsers/`: PDDL AST parsers.
  - `src/meta_planning/util/planners/madagascar/`: Embedded Madagascar SAT-based planner.
  *Thesis Role:* Serves as the primary SAT-compilation passive baseline. In our thesis, FAMA represents **Re-learning from Scratch** after a plan failure.

---

### 2.2. SAM (Safe Action Model Learning Framework)

- **Active Multi-Purpose Framework:**  
  [`https://github.com/argaman-aloni/sam_learning`](https://github.com/argaman-aloni/sam_learning)  
  *Authors:* Argaman Aloni, Roni Stern, Brendan Juba  
  *Publications Covered:*
  - *Discrete Safe Action Models:* Juba, Stern, et al. (KR 2021, ICAPS 2021)
  - *Continuous Safe Action Models:* Aloni, Stern, Juba (AAAI 2023)
  - *Conditional and Universal Effects:* Aloni, Stern (ICAPS 2024)
  *Features:*
  - Strictly learns *safe inner approximations* ($\widehat{\text{Pre}} \supseteq \text{Pre}^*$) ensuring zero false positives.
  - Includes model diagnosis routines for detecting precondition and effect violations.
  - Integrated with `pddl-plus-parser`, Metric-FF, Fast Downward, and VAL.
  *Predecessor Lifted Repo:* [`https://github.com/hsle/sam-learning`](https://github.com/hsle/sam-learning)  
  *Thesis Role:* Serves as the canonical passive safe learning baseline. Demonstrates the fundamental limitation: passive safety avoids phantom shortcuts only by being overly conservative (high false negatives, failing to find valid plans).

---

### 2.3. LOCM & LOCM2 (Learning Object-Centric Models)

- **Original Formulation:**  
  Stephen N. Cresswell, Thomas L. McCluskey, Margaret M. West (ICAPS 2009; KER 2013: "Acquiring planning domain models using LOCM").  
  *Original Implementation:* SWI-Prolog (`locm.pl`, `locm2.pl`).
- **Canonical Python Library (`macq`):**  
  [`https://github.com/AI-Planning/macq`](https://github.com/AI-Planning/macq)  
  *Maintainer:* AI-Planning community / Christian Muise (`@haz`)  
  *Core Files:*
  - `macq/extract/locm.py`: Clean, fully-featured Python reimplementation of LOCM and LOCM2.
  - `macq/extract/arms.py`: ARMS (Action-Relation Modeling System, Yang et al. 2007).
  - `macq/extract/slaf.py`: SLAF (Simultaneous Learning and Filtering, Amir & Chang 2008).
  - `macq/observation/`: Observation generators and partial-trace filters.
  *Thesis Role:* Provides the object-centric finite-state machine baseline for relational STRIPS action acquisition from plan traces without initial state annotations.

---

### 2.4. FastLAS & Inductive Logic Programming (ILP)

- **FastLAS Repository:**  
  [`https://github.com/spike-m/FastLAS`](https://github.com/spike-m/FastLAS)  
  *Author:* Mark Law (Imperial College London)  
  *Paper:* "FastLAS: Scalable Inductive Logic Programming" (KR 2020)  
  *Solver Stack:* C++ binary compiling learning tasks to Clingo (Answer Set Programming).  
  *Thesis Role:* Inductive hypothesis synthesis engine for learning Horn-clause precondition rules from positive and negative state transition counterexamples.

---

## 3. Official Benchmark Suites and Domain Generators

### 3.1. Official IPC Domain Generators
- **Repository:** [`https://github.com/AI-Planning/pddl-generators`](https://github.com/AI-Planning/pddl-generators)  
- **DOI:** [`10.5281/zenodo.6382173`](https://doi.org/10.5281/zenodo.6382173)  
- **Origin:** Jörg Hoffmann's FF domain collection and IPC benchmark committee.  
- **Key Domain Generators:**
  - `blocksworld/`: Generates $N$-block configurations with towers and tables.
  - `gripper/`: Generates $M$-room, $N$-ball, $K$-gripper transport problems.
  - `logistics/`: Generates $C$-city, $A$-airplane, $T$-truck, $P$-package distribution problems.
  - `depots/`: Combines Blocksworld stacking with Logistics truck distribution.
  - `sokoban/`: Generates push-box gridworld puzzles with obstacle constraints.

### 3.2. Fast Downward Official Benchmark Collection
- **Repository:** [`https://github.com/aibasel/downward-benchmarks`](https://github.com/aibasel/downward-benchmarks)  
- **Maintainers:** Malte Helmert, Gabriele Röger, Jendrik Seipp (University of Basel).  
- **Standard Domains Included:**
  - All competition problem sets from IPC-1998 through IPC-2018 (optimal and satisficing tracks).
  - Validated STRIPS and ADL problem files free of duplicate predicates or syntax malformations.

---

## 4. Comparison of Action Model Learning & Repair Approaches

| System | Learning Paradigm | Input Required | Soundness / Safety Guarantee | Query / Step Complexity | Repair Mechanism |
|---|---|---|---|---|---|
| **FAMA** (Aineto et al.) | Passive SAT / Classical Plan Compilation | Set of observed plan traces $\mathcal{T}$ | Exact model if traces complete; no worst-case sample bound | Requires global re-solve ($O(\text{SAT})$) | Re-learn from scratch |
| **SAM** (Juba & Stern) | Passive PAC-style Inner Approximation | State-action-next transition tuples | Safe: $\widehat{\text{Pre}} \supseteq \text{Pre}^*$ (zero false positives) | $O(|\mathcal{F}|/\epsilon \log(1/\delta))$ samples | Passive intersection |
| **LOCM2** (Cresswell et al.) | Passive Object-Centric State Machine | Action-sequence traces (no state fluents) | Induces state machines matching traces | Heuristic graph analysis | Re-extract from traces |
| **FastLAS** (Law et al.) | Active / Offline Inductive Logic Prog. | Context, positive & negative examples | Minimum cost hypothesis in language bias | Exponential in worst case ASP search | Re-synthesize hypothesis |
| **CEG-OMR** *(Ours)* | **Closed-Loop Active Counterexample Repair** | Goal task + Oracle execution feedback | **Exact convergence**: $\widehat{M} = M^*$ on reachable envelope | **Polynomial**: $K_{\text{repair}} \le k \cdot |\mathcal{F}|^r$ (Theorem 2) | **Horn-clause counterexample elimination** |

---

## 5. Integration into the Master's Thesis Pipeline

1. **Adapter Layer (`src/adapters/`):**
   - Cleaners and translators map outputs from FAMA (`fama_cleaner.py`), LOCM2 (`locm2_translator.py`), and FastLAS (`fastlas_translator.py`) to standard PDDL.
2. **Oracle Verifier (`src/repair/ceg_omr_engine.py`):**
   - Connects Fast Downward directly to the real environment simulator $M^*$, producing exact counterexample tuples $\xi_t = \langle s_t, a_t, \bot \rangle$.
3. **Four Canonical Evaluation Domains (`domains/`):**
   - **Sokoban**: Game AI spatial obstacle constraints (`(clear ?b-target)` in `push`).
   - **Blocksworld**: Classical stacking bottleneck (`(handempty)` in `pick-up`).
   - **Gripper**: Resource capacity bottleneck (`(free ?gripper)` in `pick`).
   - **Logistics**: Spatial topology containment bottleneck (`(in-city ?to ?c)` in `drive-truck`).
