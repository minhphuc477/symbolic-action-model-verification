# Game AI Research Visualization Suite & Playtesting Platform
> **Self-Adaptive Symbolic World Models for Intelligent Agents in Game Environments**  
> Publication-grade interactive web visualizer, Mind-vs-Reality telemetry console, and figure exporter.

---

## Overview

The `ui_ux/` directory hosts a standalone, publication-grade interactive playtester and scientific dashboard. Built under Linear.app and Vercel dark theme principles (deep canvas `#010102`, surface ladder `#0f1011`–`#18191a`, hairline borders, and zero raw emojis), it provides a visual testbed for game AI agents:

1. **Mind vs Reality Dual-View Playtester**:
   - **Agent Mind (World Model Belief)**: Visualizes the hallucinated shortcut trajectory (*Ghost Agent*) resulting from omitted preconditions (e.g., attempting a speedrun sequence break through a locked gate without collecting the key).
   - **Concrete Game Engine (Ground Truth Reality)**: Renders physical execution in real time with high-DPI procedural vector graphics. When an illegal action is attempted, the engine emits a physical barrier shockwave and failure tuple $\xi_{\text{failure}} = \langle s, a, \text{REJECTED} \rangle$.
2. **Online Diagnostic Repair (CEG-OMR)**:
   - Live telemetry showing automated abduction via **Precondition-Delete Effect Coherence**, patching the flawed PDDL action model on the fly and restoring 100% plan execution success rate (PESR).
3. **Deadlock & Irreversibility Safety Shield**:
   - Formal verification of action reversibility in puzzle environments (e.g., Sokoban non-goal corner pushes) to safely intercept absorbing sink states with zero physical environment queries ($K_{\text{env}} = 0$).
4. **1,080-Run Empirical Audit Matrix**:
   - Comprehensive Fast Downward solver data evaluating the Shortcut-Inducing (Regime I) vs Cost-Preserving (Regime II) dichotomy across 9 domains and 3 game genres.
5. **SOTA Game AI Radar**:
   - Comparative multi-axis radar chart benchmarking Safe CEG-OMR against SAM, FAMA, LOCM2, and FastLAS.

---

## Directory Layout

```
ui_ux/
├── assets/
│   ├── icons/                  # Crisp SVG UI icons (play, pause, step, reset, shield, cpu, etc.)
│   ├── sprites/                # Vector game sprites (hero, ghost hero, brass key, iron gate, portal)
│   └── tiles/                  # Procedural stone flagstone and masonry wall tiles
├── css/
│   └── dashboard.css           # Linear design tokens, hairline borders, monospace terminal styling
├── js/
│   ├── game_visualizer.js      # Procedural HTML5 Canvas 2D engine with requestAnimationFrame lerp
│   ├── dashboard.js            # Tab routing, telemetry binding, Chart.js radar & bar integration
│   └── topology_graph.js       # Search-tree topology graph renderer
├── data/
│   └── benchmark_data.json     # Fast Downward benchmark logs (1,080 runs, 9 domains)
├── scripts/
│   ├── generate_assets.py      # Automated SVG vector generator for UI and game sprites
│   ├── serve.py                # Zero-dependency local web server with auto-port detection
│   └── export_figures.py       # Camera-ready vector PDF & 300 DPI PNG figure generator
├── export/                     # Exported figures (Fig 1, Fig 2, Fig 3 in PDF/PNG)
├── index.html                  # Master dashboard single-page application
└── README.md                   # Documentation guide
```

---

## Quickstart & Launch

### 1. Launch the Playtesting Dashboard
Run the launcher script to start a local server and open the interface:
```bash
python ui_ux/scripts/serve.py
```
*Access in browser*: `http://localhost:8080` (or `http://localhost:8081` if port 8080 is in use).

### 2. Regenerate SVG Assets
To regenerate or inspect vector assets:
```bash
python ui_ux/scripts/generate_assets.py
```

### 3. Export Publication-Ready Figures
To generate vector PDF and 300 DPI PNG figures for paper submission:
```bash
python ui_ux/scripts/export_figures.py
```

---

## Design Standards & Commitments

- **Zero Raw Emojis**: All entities, controls, and HUD elements use clean SVG vector icons or high-DPI procedural Canvas 2D rendering.
- **Smooth Animation Interpolation**: Character movement uses a continuous lerp function ($x_{t+1} = x_t + \alpha (x_{\text{target}} - x_t)$) with $60$ FPS `requestAnimationFrame` updates.
- **Verified Empirical Data**: Every number and graph displayed in the dashboard is tied to reproducible solver executions across the 1,080 Fast Downward test runs.
