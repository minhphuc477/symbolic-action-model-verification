# Connected Papers Literature Flows & Citation Network (2021–2026)

> [!NOTE]
> This document maps out the connected papers network, explicit citation flows, and research lineages across **World Models**, **Action Model Learning**, **Quality-Diversity (PCG-QD)**, and **General Game Playing / Rule Interventions**.

---

## 1. Citation Lineage 1: World Models, Value Equivalence & Planning Adequacy

```mermaid
flowchart TD
    WM18["Ha & Schmidhuber (2018)<br/>World Models"] --> Dreamer19["Hafner et al. (2019/2023)<br/>Dreamer V1 / V3"]
    WM18 --> MuZero20["Schrittwieser et al. (2020)<br/>MuZero: Master Games Without Rules"]
    MuZero20 --> VE21["Grimm et al. (2020, 2021)<br/>Value Equivalence & Proper VE"]
    VE21 --> CausalJEPA26["Nam et al. (ICML 2026)<br/>Causal-JEPA: Object Latent Masking"]
    VE21 --> Aguilar26a["Aguilar Martín (July 2026, arXiv:2607.14169)<br/>Verified-vs-Correct Gap in Code World Models"]
    Aguilar26a --> Aguilar26b["Aguilar Martín (Aug 2026, arXiv:2608.17956)<br/>Quantitative Law of Danger"]
    Aguilar26b --> Aguilar26c["Aguilar Martín (Sep 2026, arXiv:2608.28541)<br/>Counterexample-Guided Tree Search"]
```

### Core Connection Mechanics:
- **Value Equivalence (Grimm et al. 2020/2021)**: World models need not match exact state transitions if they preserve value predictions under optimal policy $\pi^*$.
- **The Verified-vs-Correct Gap (Aguilar Martín 2026)**: Passive transition accuracy ($\ge 98\%$) masks omitted pivotal rules on unvisited tree branches, causing 100% play loss ($B = 0.091, 95\%\text{ CI }[0.065, 0.117]$).

---

## 2. Citation Lineage 2: Action Model Learning & Code World Models

```mermaid
flowchart TD
    AML13["Jiménez et al. (2012) / Cresswell (2013)<br/>Action Model Learning in PDDL"] --> PDDLGym20["Silver et al. (2020)<br/>PDDLGym: Gym Envs for Planning"]
    PDDLGym20 --> GIFMCTS25["Dainese et al. (2025)<br/>GIF-MCTS: Symbolic Action Tracing"]
    GIFMCTS25 --> CWM26["Aguilar Martín (2026, arXiv:2607.14169)<br/>Active Search-Tree Probing for CWM"]
    PDDLGym20 --> RuleInfer26["Xiang et al. (April 2026, arXiv:2604.24062)<br/>Decontextualized Causal Schemas"]
```

### Core Connection Mechanics:
- **Symbolic Action Models vs Neural Code World Models**: PDDLGym established structured state-action learning. Modern Code World Models generate executable Python/JAX transition code, requiring active search-tree probing to verify rule correctness.

---

## 3. Citation Lineage 3: Procedural Content Generation & Quality-Diversity (PCG-QD)

```mermaid
flowchart TD
    MAP15["Mouret & Clune (2015) / Pugh (2016)<br/>MAP-Elites Foundation"] --> PCGRL20["Khalifa et al. (2020)<br/>PCG-RL: Controllable PCG via RL"]
    MAP15 --> CMAME21["Fontaine et al. (2021, 2023)<br/>CMA-ME: Covariance Matrix Adaptation MAP-Elites"]
    PCGRL20 --> IllumRL21["Earle et al. (2021)<br/>Illuminating Reinforcement Learning"]
    CMAME21 --> Mortar25["Mortar / QD Engine (2025)<br/>Quality Diversity Level & Rule Generation"]
```

### Core Connection Mechanics:
- **Quality-Diversity as Environment Probing**: MAP-Elites and CMA-ME generate diverse game levels/rules that serve as stress tests for world model planning adequacy.

---

## 4. Citation Lineage 4: General Game Playing & Paired Rule Interventions

```mermaid
flowchart TD
    GGP05["Genesereth et al. (2005)<br/>General Game Playing GDL"] --> PS13["Lavox (2013)<br/>PuzzleScript Engine & Grid DSL"]
    PS13 --> MDPPlay19["Gygli et al. (2019)<br/>MDP Playground Testbed"]
    MDPPlay19 --> MirrorCraft26["Gao et al. (July 2026, arXiv:2607.29218)<br/>MirrorCraft: Paired Server-Side Rule Interventions"]
    PS13 --> G078R["Thesis G078-R (2026)<br/>External Executable Rule Intervention Harness"]
```

### Core Connection Mechanics:
- **Rule Intervention Sensitivity**: MirrorCraft proves static agents collapse under paired server-side rule modifications, highlighting the necessity of causal execution feedback over passive prompt context.

---

## 5. Master Connected Papers Matrix

| Paper / Reference | Year | Lineage | Core Citation Dependency | Primary Contribution to Thesis |
|---|---|---|---|---|
| **Aguilar Martín (arXiv:2607.14169)** | 2026 | World Models | MuZero / Value Equivalence | Verified-vs-Correct Gap in Code World Models |
| **Gao et al. (arXiv:2607.29218)** | 2026 | Rule Interventions | General Game Playing / MDP Playground | Paired server-side rule intervention benchmark |
| **Nam et al. (ICML 2026)** | 2026 | World Models | JEPA / Object Representation | Latent object masking for causal world models |
| **Xiang et al. (arXiv:2604.24062)** | 2026 | Action Models | PDDLGym / Symbolic Planning | Decontextualized causal schemas & rule transfer |
| **Dainese et al. (2025)** | 2025 | Action Models | MCTS / Code Generation | GIF-MCTS active search-tree rollouts |
| **Grimm et al. (2020, 2021)** | 2021 | World Models | RL Value Function Theory | Value Equivalence and Proper Value Equivalence |
| **Fontaine et al. (2021, 2023)** | 2023 | PCG-QD | MAP-Elites | CMA-ME quality diversity optimization |
| **Silver et al. (2020)** | 2020 | Action Models | PDDL / OpenAI Gym | PDDLGym benchmark for action model learning |
| **Hafner et al. (2019, 2023)** | 2023 | World Models | Latent Dynamics Models | Dreamer V1/V2/V3 latent world model architecture |
