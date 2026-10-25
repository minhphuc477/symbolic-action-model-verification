# 🎨 UI/UX Research Visualization Suite
> **Search-Tree Topology Collapse & Safe CEG-OMR Interactive Platform**  
> Comprehensive interactive dashboard, graph visualizer, and publication figure exporter for master's thesis research.

---

## 🌟 Overview

The `ui_ux/` directory provides an interactive, standalone web dashboard and automated figure export pipeline designed to visualize all theoretical, empirical, and architectural aspects of the thesis:
1. **Interactive State-Space Topology ($TS = (S, E)$)**: Dynamic HTML5 Canvas rendering of Hoffmann local search topology, Heuristic Seduction under delete relaxation, and branch divergence $\Omega(b^{D-d})$.
2. **1,080-Run Regimes Audit Matrix**: Interactive exploration of Regime I ($\Delta c > 0$, 100% collapse) vs Regime II ($\Delta c = 0$, 44.8% collapse / 0% ontable) across 9 domains.
3. **Reversibility Safety Shield Telemetry**: Live inspection of action reversibility (Reversible vs Irreversible) and zero-risk virtual interception ($K_{\text{env}} = 0$).
4. **SOTA Multi-Metric Radar**: Comparative radar and bar charts against SAM, FAMA, LOCM2, FastLAS, and CLaP.
5. **Publication Figure Exporter**: One-click generation of 300 DPI PNG and scalable vector PDF figures for camera-ready ICAPS / AAAI submissions.

---

## 🚀 Quickstart & Usage

### 1. Launch the Interactive Web Dashboard
Run the built-in launcher script. It automatically boots a local HTTP server and opens the dashboard in your default browser:
```bash
python ui_ux/scripts/serve.py
```
*Accessible directly in your browser at*: `http://localhost:8080` (or `http://localhost:8081` if port 8080 is busy).

### 2. Export Publication-Ready Figures (Vector PDF & 300 DPI PNG)
To regenerate all figures into `ui_ux/export/` for inclusion in LaTeX papers:
```bash
python ui_ux/scripts/export_figures.py
```
Generated artifacts:
- `ui_ux/export/fig1_regime_dichotomy.pdf` & `.png`
- `ui_ux/export/fig2_sota_pesr_comparison.pdf` & `.png`
- `ui_ux/export/fig3_safety_shield_interception.pdf` & `.png`

---

## 📂 Directory Layout

```
ui_ux/
├── index.html                   # Master single-page interactive dashboard
├── css/
│   └── dashboard.css            # Modern dark-mode scientific UI styling
├── js/
│   ├── dashboard.js             # Data binding, tab switching, Chart.js integrations
│   └── topology_graph.js        # Native HTML5 Canvas 2D graph renderer & particle engine
├── data/
│   └── benchmark_data.json      # Structured experimental data from 1,080 runs & 9 domains
├── scripts/
│   ├── serve.py                 # Local server launcher with automatic browser opening
│   └── export_figures.py        # Vector PDF and 300 DPI matplotlib figure generator
├── export/                      # Exported publication figures (PDF / PNG)
└── README.md                    # This documentation guide
```

---

## 🔬 Interactive Dashboard Tabs

- **Tab 1: Search Topology & Seduction**:
  - Live interactive graph showing physical paths vs spurious shortcut branches.
  - Interactive hover tooltips displaying $g(s)$, true heuristic $h^*(s)$, and seduced heuristic $\hat{h}(s)$.
  - Toggle button to enable/disable Heuristic Seduction in real time.
  - Interactive slider computing the lower-bound node expansion $\Omega(b^{D-d})$.
- **Tab 2: 1,080-Run Regimes Audit**:
  - Bar chart comparing $A^*$ LM-Cut, Blind BFS, and GBFS across Regimes I and II.
  - Full matrix table for 9 domains: *Blocksworld, Gripper, Logistics, Sokoban, Pitch Black, Dungeon Escape, Barman, Rovers, Depots*.
- **Tab 3: Reversibility Safety Shield**:
  - Visual decision rule: Dispatch vs Intercept.
  - Action telemetry showing static inverse operator existence and non-renewable fact consumption.
- **Tab 4: SOTA Baseline Radar**:
  - 5-axis radar chart evaluating PESR, syntactic accuracy, Family B solvability, query efficiency, and safety.
  - Detailed limitations analysis of SAM, FAMA, LOCM2, FastLAS, and CLaP.
- **Tab 5: Mathematical Foundations**:
  - Formal KaTeX theorem cards for Heuristic Seduction (Theorem 1) and Polynomial Active Complexity (Theorem 2).
