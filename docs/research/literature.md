# Literature map (rebuild, verified 2026-10-26)

Verification levels:

- **M** — bibliographic metadata (title, authors, venue, year) confirmed via archival search
  (AAAI, IJCAI, ICAPS, KR, NeurIPS, Elsevier, DBLP, OpenReview, arXiv).
- **F** — full text read and checked line-by-line in this session.
- **C** — source code cloned and inspected directly (`external/AMLGym`).

## 1. Directly competing work (repair of an *existing* flawed domain)

| Key | Paper | Level | Verified findings & scope | Relation to our work |
|---|---|---|---|---|
| `Lin2023AAAI` | S. Lin, A. Grastien, P. Bercher. *Towards Automated Modeling Assistance: An Efficient Approach for Repairing Flawed Planning Domains.* AAAI 2023, pp. 12022–12031. DOI `10.1609/aaai.v37i10.26418`. | M | Computes cardinality-minimal repairs via Model-Based Diagnosis / Hitting Set so a known-valid plan succeeds; handles lifted schemas and negative preconditions. | Offline: takes a valid plan as input. Minimum-cardinality repair itself is **not** novel and must be cited to Lin et al. |
| `Lin2025AAAI` | S. Lin, A. Grastien, R. Shome, P. Bercher. *Told You That Will Not Work: Optimal Corrections to Planning Domains Using Counter-Example Plans.* AAAI 2025. | M | Extends optimal minimal-cardinality repair to both positive plans and negative counter-example plans via conflict / hitting-set / MaxSAT formulation; evaluated on Fast Downward benchmarks with random injected errors. | Strongest offline counterpart. Note: legacy `references.bib` misnamed R. Shome; corrected. Takes plans offline rather than acquiring observations interactively under partial/binary feedback. |
| `Gragera2023ICAPS` | A. Gragera, R. Fuentetaja, Á. García-Olaya, F. Fernández. *A Planning Approach to Repair Domains with Incomplete Action Effects.* ICAPS 2023. | M | Compiles an unsolvable task into an extended task where actions can insert missing effects, solved by an off-the-shelf classical planner without user input. | Overlaps with planner-side relaxation of unsolvable tasks (focused on incomplete effects, without environment verification). |
| `Patel2026NEmo` | P. Patel, K. S. Bukkapatnam. *Policy-Induced Blind Spots in Symbolic Action-Model Repair.* NEmo Workshop @ NeurIPS 2026 (OpenReview). | M | Proves passive policies that only execute actions believed applicable have 0 probability of exposing spurious preconditions (0/200 vs 197/200 for diagnostic policies). | Directly establishes that passive lockout on spurious preconditions is known; we must cite them rather than claiming lockout discovery as novel. |

## 2. Version-space and online/offline action model learning

| Key | Paper | Level | Verified findings & scope |
|---|---|---|---|
| `Aineto2024KR` | D. Aineto, E. Scala. *Action Model Learning with Guarantees.* KR 2024 (`arXiv:2404.09631`). | **F** | Formalises version spaces $\mathcal{V}_{\mathcal{H}^a_p}, \mathcal{V}_{\mathcal{H}^a_e}$ under full observability (Theorems 1, 2, 4). Proves lower bound $L$ yields optimal sound models (SAM, Theorem 11) and upper bound $U$ yields optimal complete FOND models (Theorem 12). Explicitly notes in Sections 6–7 that (i) models *between* the sound and complete extremes and (ii) *active* version-space learning remain open future work. |
| `Juba2021KR` | B. Juba, H. S. Le, R. Stern. *Safe Learning of Lifted Action Models.* KR 2021, pp. 379–389. | M + **C** (`AMLGym`) | Offline lifted SAM: preconditions = intersection of pre-states; effects = observed state deltas. |
| `Lamanna2021IJCAI` | L. Lamanna, A. Saetti, L. Serafini, A. E. Gerevini, P. Traverso. *Online Learning of Action Models for PDDL Planning.* IJCAI 2021, pp. 4112–4118. DOI `10.24963/ijcai.2021/566`. | M + **C** (`AMLGym`) | OLAM: online learning from an empty prior by planning towards informative states. |
| `Lamanna2025AIJ` | L. Lamanna et al. *Lifted Action Models Learning from Partial Traces.* Artificial Intelligence 339:104256, 2025. | M + **C** (`AMLGym`) | OffLAM: offline learning under partial state observability. |
| `Verma2021AAAI` | P. Verma, S. R. Marpally, S. Srivastava. *Asking the Right Questions: Learning Interpretable Action Models Through Query Answering.* AAAI 2021, pp. 12024–12033. | M | Active plan-query learning of a black-box simulator's STRIPS model from scratch. |
| `AMLGym` | L. Lamanna, R. Stern, et al. `github.com/LamannaLeonardo/AMLGym` + Stern et al. KEPS @ ICAPS 2025. | **C** | Reference benchmark (25 IPC domains with separate `learning/` and `solving/` splits) and 3 metric suites (`_syntactic.py`, `_predictive.py`, `_solving.py`), plus `RandomAgent.py` (uniform random ground actions + SAM). |

## 3. World models, LLM domain generation, and prediction-vs-planning mismatch

| Key | Paper | Level | Verified findings & scope |
|---|---|---|---|
| `Martin2026ArXiv` | J. Aguilar Martín. *When a Verified World Model Still Loses: Play-Adequacy vs. Prediction-Accuracy in LLM-Synthesized Code World Models.* `arXiv:2607.14169v2`, Jul 2026. | **F** | Shows ≥98% state-accurate models systematically lose at play when omitting rare pivotal rules; proves Bernoulli gate-miss factor $(1-\text{rarity})^N$ and shows empirically (Section 5) that feeding example transitions back to LLMs fails to recover omitted rules ("translation, not inference"). |
| `Mahdavi2024NeurIPS` | S. Mahdavi, R. Aoki, K. Tang, Y. Cao. *Leveraging Environment Interaction for Automated PDDL Translation and Planning with Large Language Models.* NeurIPS 2024. | M | Iterative LLM PDDL refinement using Exploration Walk feedback (66% solve rate across 10 domains). Motivates repairing flawed symbolic priors via environment interaction. |
| `Tang2024WorldCoder` | H. Tang, D. Key, K. Ellis. *WorldCoder, a Model-Based LLM Agent.* NeurIPS 2024. | M | Synthesises Python world models online using optimism under uncertainty. (Note: legacy `.bib` falsely attributed WorldCoder to Grand et al. ICML 2025; fixed.) |

## 4. Errors found and purged from legacy bibliography

1. Fabricated paper `Karia2024ICAPS` ("CLaP: Counterexample-Guided Learning of Action Models") replaced by Karia et al.'s real ICAPS 2024 paper (*Epistemic Exploration...*).
2. Fabricated citation `Grand2025ICML` for WorldCoder replaced by Tang, Key, Ellis (NeurIPS 2024).
3. Wrong author name `Tathagata Shome` in `Lin2025AAAI` corrected to `Rahul Shome`.
4. Wrong venue/pages for `Cresswell2013` and wrong pages for `Aineto2019AIJ` corrected.
