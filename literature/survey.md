# Master Literature Survey: World Models & Planning Adequacy in Games (2024–2026)

## Pillar 1: Code World Models & Active Search-Tree Verification

### 1. Aguilar Martín (July 2026) — *When a Verified World Model Still Loses* (arXiv:2607.14169)
- **Focus**: Play-Adequacy vs. Prediction-Accuracy in LLM-Synthesized Code World Models.
- **Finding**: Proves CWMs achieving 100% transition accuracy and >=98% search-distribution state accuracy still lose 100% of gameplay trials due to pivotal rule omissions.
- **Relevance**: Core empirical counter-anchor for G078-R thesis.

### 2. Aguilar Martín (August 2026) — *An Omitted Mode Is a Rare Rule* (arXiv:2608.17956)
- **Focus**: The Sampling-Verification Danger Law in Continuous Code World Models.
- **Finding**: Formalizes $\text{danger} = \text{play\_cost} \times (1 - r)^N$, proving exponential sampling blind spots.
- **Relevance**: Mathematical foundation for sampling gate failure.

### 3. Aguilar Martín (September 2026) — *An Enclosed Mode Is a Gauge Choice* (arXiv:2608.28541)
- **Focus**: Topology Relative to Reach in Certified Code World Models.
- **Finding**: Unreached state spaces act as unconstrained gauge variables under passive gates.
- **Relevance**: Topological argument for active counterexample-guided tree search.

### 4. Dainese et al. (2025) — *GIF-MCTS: LLM Code World Models guided by MCTS* (arXiv:2410.17859)
- **Focus**: Generating Code World Models with MCTS feedback.
- **Finding**: Uses active MCTS execution feedback to debug and synthesize Python Code World Models.
- **Relevance**: Algorithmic baseline for active verification.

### 5. Schwoebel et al. (September 2026) — *World-Time Compute with Verified Code World Models* (arXiv:2609.09163)
- **Focus**: Synthetic trajectory rollouts from symbolic Code World Models.
- **Finding**: Fine-tuning on verified symbolic CWM traces lifts generalization by +29 points and eliminates 20-step compounding errors.
- **Relevance**: Training paradigm for zero-shot generalization.

---

## Pillar 2: Structural Mediators & Causal Abstraction in Reinforcement Learning

### 1. Nam et al. (ICML 2026 Accepted) — *Causal-JEPA: Learning World Models through Object-Level Latent Masking* (arXiv:2602.11389)
- **Authors**: Nam, Le Lidec, Maes, LeCun, Balestriero.
- **Focus**: Latent causal world models via object-level latent masking.
- **Finding**: Establishes structural causal abstractions over object interactions for zero-shot interventional predictions.
- **Relevance**: Architecture foundation for Paper 2 (Causal-Fidelity World Models).

### 2. Xiang et al. (April 2026) — *Grounding Before Generalizing* (arXiv:2604.24062)
- **Authors**: Xiang, Ma, Cao, Zhu, Zhu.
- **Focus**: Human vs AI Causal Transfer in OpenLock.
- **Finding**: Shows AI agents lack decontextualized causal schemas and require initial environmental grounding before structural transfer.
- **Relevance**: Explains zero-shot transfer failure in static LLMs.

### 3. Xia & Bareinboim (2024/2025) — *Causal Abstraction Inference under Lossy Representations* (arXiv:2409.17387)
- **Focus**: Projected causal abstractions in high-dimensional RL.
- **Finding**: Gives graphical identifiability criteria for interventional queries across abstraction levels.
- **Relevance**: Formal theory for causal state aggregation.

---

## Pillar 3: Paired Minimal Rule Interventions & Zero-Shot Rule Transfer

### 1. Gao et al. (July 2026) — *MirrorCraft: Paired Evaluation under Hidden Rule Changes* (arXiv:2607.29218)
- **Focus**: Paired evaluation in Minecraft (Vanilla vs. Mirror).
- **Finding**: Server-side rule interventions cause complete agent collapse; text rule descriptions yield minimal gains without active execution.
- **Relevance**: 3D environment counterpart to 2D PuzzleScript rule interventions.

### 2. Lima Neto et al. (2025/2026) — *Python Agent in Ludii* (IEEE Transactions on Games)
- **Focus**: General Game Playing interface for Ludii.
- **Finding**: Benchmarks MCTS and symbolic agents under dynamic rule transfer across combinatorial games.
- **Relevance**: Substrate reference for General Game Playing.
