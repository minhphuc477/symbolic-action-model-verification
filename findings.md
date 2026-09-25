# Findings & Evolving Narrative Synthesis

## 1. Current Understanding (What We Know So Far)
- **Verified-vs-Correct Gap (Passive Prediction != Active Planning)**:
  - **Aguilar Martín (July 2026, arXiv:2607.14169)**: Demonstrates that Code World Models achieving 100% transition accuracy and >=98% state accuracy on passive validation sets lose 100% of actual gameplay trials due to pivotal rule omissions on unvisited search-tree branches.
  - **Aguilar Martín (Aug 2026, arXiv:2608.17956)**: Formalizes the Quantitative Law of Danger: $\text{danger} = \text{play\_cost} \times (1 - r)^N$, proving exponential blind spots for rare pivotal rules under passive validation gates.
  - **Aguilar Martín (Sep 2026, arXiv:2608.28541)**: Shows unreached state spaces act as unconstrained gauge variables under passive gates, proving active counterexample-guided tree search is necessary for model certification.

- **Paired Rule Intervention Sensitivity & Zero-Shot Transfer**:
  - **Gao et al. (July 2026, arXiv:2607.29218 - MirrorCraft)**: Demonstrates that static agents collapse under paired server-side rule modifications (Rule Intervention Effect), and text rule descriptions yield minimal gains without active causal execution.
  - **Xiang et al. (April 2026, arXiv:2604.24062)**: Proves current AI agents lack decontextualized causal schemas and require initial environmental grounding before structural causal transfer can occur.
  - **Nam et al. (ICML 2026, arXiv:2602.11389 - Causal-JEPA)**: Establishes object-level latent masking to construct latent causal world models for zero-shot interventional predictions.

## 2. Patterns and Insights
- **Rule Translation vs Rule Inference**:
  LLMs act as rule translators from prompt context rather than inductive dynamics inferencers. Scaling model size (GPT-5 class) or applying off-policy DAgger does not fix pivotal omissions without active search-tree coverage.
- **Active Search-Tree Probing**:
  Frameworks like GIF-MCTS (Dainese et al. 2025) and World-Time Compute (Schwoebel et al. 2026) show that incorporating active MCTS rollouts and symbolic code world model traces eliminates error compounding and improves generalization.

## 3. Lessons and Constraints
- **Constraint 1**: Never use passive transition prediction accuracy as a surrogate for planning competence.
- **Constraint 2**: Always evaluate world models under paired minimal rule interventions to isolate causal dynamic learning from spatial/layout memorization.
- **Constraint 3**: Purge MDPI and low-rigor journals from core thesis citations; anchor all theoretical claims on tier-A/A* literature (NeurIPS, ICLR, ICML, AAAI, IJCAI, ICAPS, IEEE ToG, AIJ).

## 4. Open Questions & Hypotheses
- Can active search-tree frontier sampling reduce sample complexity from $O(b^{d_{\max}})$ to $O(|R_{\text{causal}}|)$?
- How do Structural Mediators and Causal Abstractions enable zero-shot rule transfer under hidden rule changes?
