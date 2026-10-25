---
name: scientific-theory-and-paper-architect
description: Master research methodology, unbiased experimental auditing, result-to-claim mechanical verification, and academic paper craftsmanship for top-tier AI venues (ICAPS, AAAI, IJCAI, JAIR, NeurIPS). Use when designing unbiased experiments, verifying claims against solver logs, auditing threats to validity, compiling LaTeX manuscripts, or generating publication-ready figures.
metadata:
  model: inherit
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 🎓 Scientific Theory & Paper Architect

A premier meta-research skill dedicated to upholding strict scientific integrity, preventing experimental bias, mechanically verifying manuscript claims against solver logs, and structuring top-tier academic manuscripts.

---

## 1. Principles of Scientific Integrity & Unbiased Inquiry

A scientific contribution is defined not by optimistic claims, but by **reproducible empirical proof** and **uncompromising boundary conditions**.

```
    ┌────────────────────────────────────────────────────────┐
    │        Hypothesis Formulation & Mathematical Model      │
    └───────────────────────────┬────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │        Unbiased Experimental Matrix Design             │
    │  • Multi-domain breadth (Blocksworld, Gripper, etc.)   │
    │  • Regime I (Δc > 0) vs Regime II (Δc = 0) partition    │
    │  • Multiple search algorithms (A* LM-Cut, GBFS, Blind) │
    └───────────────────────────┬────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │        100% Real Solver Execution (Zero Mock Data)     │
    │  • Fast Downward / Madagascar / Clingo solver logs     │
    │  • Structured JSON telemetry (time, nodes, PESR)       │
    └───────────────────────────┬────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │        Result-to-Claim Mechanical Audit                │
    │  • 1-to-1 assertion match (Paper Claim ↔ Log Value)   │
    │  • Verification gate: 5/5 Claims Checked               │
    └───────────────────────────┬────────────────────────────┘
                                │
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │        Publication-Grade Camera-Ready Manuscript       │
    │  • KaTeX / LaTeX formal math                           │
    │  • Vector PDF figures & 300 DPI publication plots       │
    │  • Balanced Discussion: Limitations & Future Work      │
    └────────────────────────────────────────────────────────┘
```

### Core Invariants (`RESEARCH_RULES.md`)
1. **Zero Fake Metrics & Zero Mock Data**: Never generate synthetic or estimated benchmark numbers. Every figure in a table or claim must be parsed from completed solver runs.
2. **Zero Mathiness**: Mathematical symbols ($TS, \Delta c, \Omega(b^{D-d}), \rho$) must correspond to exact algorithmic operations and graph-theoretic objects, not decorative pseudo-math.
3. **Regime Delineation**: Never claim universal collapse without specifying the regime. For instance, acknowledge that shortcut-inducing omissions ($\Delta c > 0$) cause 100% collapse under $A^*$, whereas cost-preserving omissions ($\Delta c = 0$) do not.
4. **Adversarial Baseline Comparison**: Compare against the strongest available competitive baselines (FAMA, LOCM2, FastLAS, SAM, CLaP, Lin et al.) under identical observational budgets.

---

## 2. Standard Evaluation Metrics in Automated Planning & AML

When reporting experimental results for ICAPS / AAAI / JAIR, adhere to the standard metric suite:

| Metric | Symbol | Formal Definition | Desired Value |
| :--- | :---: | :--- | :---: |
| **Plan Execution Success Rate** | $\text{PESR}$ | $\frac{1}{|T|} \sum_{\Pi \in T} \mathbb{I}(\text{exec}(\hat{\pi}_{\Pi}, \mathcal{M}^*) = \text{SUCCESS})$ | $100\%$ |
| **Environment Step Budget** | $K_{\text{env}}$ | Total physical steps executed in real environment | Minimal |
| **Planner Call Count** | $N_{\text{plan}}$ | Total invocations of internal planner | Polynomial |
| **Syntactic Edit Distance** | $d_{\Delta}$ | $\|\hat{\mathcal{M}} \ominus \mathcal{M}^*\|_1 = |\text{pre}_{\Delta}| + |\text{eff}_{\Delta}|$ | Minimal ($0$) |
| **1-Step Prediction Accuracy** | $A_{\text{pred}}$ | $\mathbb{E}_{(s,a)\sim \mathcal{D}} [\mathbb{I}(\hat{T}(s,a) = s')]$ | $\ge 95\%$ |
| **Polynomial Expansion Ratio** | $\rho$ | $\frac{K_{\text{env}}(\text{CEG-OMR})}{K_{\text{env}}(\text{Optimal Active Gate})}$ | $O(\text{poly}(n))$ |

---

## 3. When to Use This Skill

- When designing experimental benchmark suites to guarantee unbiased coverage across domains.
- When performing the **Result-to-Claim Mechanical Audit** on a paper manuscript.
- When checking LaTeX math syntax, symbol consistency, and citation accuracy (DOIs, archival venues).
- When formatting or refactoring academic manuscripts into camera-ready ICAPS/AAAI formats.
- When generating publication-ready matplotlib figures (vector `.pdf`, 300 DPI `.png`, correct fonts).
- When formulating responses to peer review (Rebuttal drafts).

## Do Not Use This Skill When
- Running low-level PDDL mutations or syntax parsing (use `symbolic-world-model-laboratory`).
- Inspecting raw heuristic local minima on graph nodes (use `search-space-topology-analyst`).
- Running active multi-fault abduction loops (use `counterexample-guided-rule-repair`).

---

## 4. Operational Audit Workflow

### Step 1: Claim Extraction & Normalization
Extract all quantitative claims from the manuscript (e.g. `docs/UNIFIED_FLAGSHIP_MANUSCRIPT.md`):
- *Claim 1*: "Passive AML models with $A_{\text{pred}} \ge 96\%$ yield $\text{PESR} = 0\%$ under $A^*$ heuristic search."
- *Claim 2*: "In Regime I ($\Delta c > 0$), search-tree topology collapse occurs in 100% of tested instances."
- *Claim 3*: "CEG-OMR recovers $\text{PESR} = 100\%$ within $K_{\text{env}} \le O(k \cdot |\mathcal{A}|)$ environment queries."
- *Claim 4*: "Offline planner-unsolvability backtracking refutes spurious hypotheses with $K_{\text{env}} = 0$."
- *Claim 5*: "Under partial observability $\gamma \ge 0.8$, repair convergence remains $\ge 90\%$."

### Step 2: Mechanical Log Verification
Run the verification harness:
```bash
python main.py --experiment audit
```
For each claim, read the raw benchmark output JSON files:
- Verify that sample size $N \ge 100$ per test condition.
- Confirm exact percentage matching (e.g. 1,080 / 1,080 solver runs recorded in `benchmark_outputs/`).
- Verify that standard deviation / confidence intervals are reported where appropriate.

### Step 3: Academic Tone & Nuance Verification
Audit the prose against scientific writing standards:
- **Disallowed Language**: "effortlessly", "miraculously", "revolutionary", "flawless", "unprecedented", "game-changing".
- **Required Framing**: Conservative, precise, explicitly bounded:
  - "Empirical results demonstrate..."
  - "Under the conditions of Definition 3..."
  - "A key limitation of this approach is..."
  - "In contrast to prior work which assumes..."

### Step 4: Publication Artifact Compilation
1. Check LaTeX code for KaTeX / pdfLaTeX compatibility:
   - Ensure math formulas use `$...$` or `$$...$$` with correct escaping.
   - Verify table column alignment (`l r c`) and `booktabs` styling (`\toprule`, `\midrule`, `\bottomrule`).
2. Generate publication figures with consistent typographic scale:
   - Font family: Serif (Computer Modern or Times).
   - Figure resolution: 300 DPI raster or scalable vector PDF.
   - Distinct color palettes (accessible for colorblindness).

---

## 5. Verification Checklist & Anti-Hallucination Guardrails

- [ ] **Exact Number Match**: Every number in the abstract, tables, and narrative must match `benchmark_outputs/*.json` exactly.
- [ ] **No Hidden Cherry-Picking**: If an action omission did not cause collapse (e.g., `(ontable ?x)` in `pick-up`), state so openly and explain the mathematical reason ($\Delta c = 0$).
- [ ] **Citation Verification**: Every citation must have a verified author list, venue, year, and DOI/arXiv identifier.
