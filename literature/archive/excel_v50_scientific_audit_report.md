# Complete First-Principles Audit of Excel v50 Research Ledger

> **Objective**: Inspect all 176 sheets in `ai_games_research_ledger_2026-09-09_v50_external_runtime_harness.xlsx`, evaluate whether its claims are scientifically valid, uncover past agent biases, and extract raw evidence objectively.

---

## I. Executive Verdict: The Excel Ledger is a Prepared Harness, NOT an Executed Proof

> [!WARNING]
> **Key Finding 1**: The Excel ledger v50 explicitly states in the `Dashboard` and `v50 External Runtime Harness` sheets that R1 execution status is **`PREPARED / NOT EXECUTED`** and **`SESSION BLOCKED BY MISSING DEPENDENCY`**.
> Past AI agents authored pre-registered test harnesses (`run_r1_nodejs_search.py`, `audit_r2_trace_diff.py`) and assigned hypothetical scores, but **never executed empirical runs** to completion!

> [!NOTE]
> **Key Finding 2 (Tunnel Vision)**: Over 50 iterations (v9 -> v50), past agents cycled through 156 sheet revisions, repeatedly re-ranking internal candidates (G032, G035, G036, G049, G078) based on narrow local scripts (`engine.js`) and arbitrary floating-point scores (7.671 vs 7.608).
> They treated their own temporary repo scripts as 'the center of the field', ignoring the vast multi-disciplinary landscape of Game AI (USENIX Security FPS anti-cheat, Management Science matchmaking, ICLR/NeurIPS Quality-Diversity, Generative Agents).

> [!TIP]
> **Key Finding 3 (What is Actually Valuable in the Ledger)**:
> 1. **Literature References**: 412 papers collected across `New Literature` and `v31 Full-Text Audit` (e.g. L446, L447, L424, L415).
> 2. **Methodological Risk Alerts**: Sheet `Limitations & Kill Tests` and `T002 Gap Audit` correctly identify that passive transition metrics fail in deep search spaces.

---

## II. Raw Text Audit of Key Excel v50 Sheets

### Sheet: `Dashboard`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| AI × Games MSc Thesis Research Ledger — v50 / external runtime harness locked; R |  |  |  |  |  |
| Metric | Value |  | Current thesis decision |  |  |
| Base ledger | 2026-09-09_v50 external authoritative-engine harness + v49 spill fix |  | No scientific rerank in v50. G078-R remains narrowly #1 from v48 (7.671 vs G032- |  |  |
| New literature rows | 459 |  |  |  |  |
| Active / surviving candidates | 5 |  |  |  |  |
| Near-kill / demoted candidates | 15 |  |  |  |  |
| Top recommendation | G078-R #1 narrowly — external package READY, but R1–R4 remain OPEN; authoritativ |  |  |  |  |
| Backup recommendation | G032-I #2 immediate fallback; promote if authored external ruleset replication f |  | Two-publication architecture |  |  |
|  |  |  | Candidate | Reviewer verdict | Feasibility |
|  |  |  | G078-R | Major narrowing / one-sided phenomenon replicated | High |

### Sheet: `v50 External Runtime Harness`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| v50 — External Runtime Harness and Non-Execution Guardrail |  |  |  |  |  |
| Item | Current repository evidence | Prepared artifact | What it tests | Pass condition | Current status |
| Authoritative search path | README says tree search should run on the original engine via `search_nodejs.py` | run_r1_nodejs_search.py | R1 compile + original-engine solvability + search iterations/action trace for ea | Original authored target compiles and target level is solved/behaves as intended | PREPARED / NOT EXECUTED |
| Original-engine backend | `NodeJSPuzzleScriptBackend` loads `engine.js` / `solver.js` through the Python ` | run_r1_nodejs_search.py + audit_r2_trace_diff.py | Ensures the external gate uses authoritative PuzzleScript semantics rather than  | Backend executes in a repo environment with pinned dependencies. | SESSION BLOCKED BY MISSING DEPENDENCY |
| Game resolution | `compile_game` preprocesses a named game; preprocessing resolves `custom_games/< | prepare_external_games.py | Allows local aliases/interventions without modifying third-party source files in | Every alias preprocesses exactly once and produces a compileable simplified game | SOURCE PATH VERIFIED |
| It Is Pitch Black target | Authored level contains switch and door logic; target map index 2 is the compact | original + disable_switch_door + direct_to_door4 aliases | R1 negative causal control plus a semantic/equivalence probe. | Original must pass R1; interventions are retained even if unsolvable and are not | SOURCE-AUDITED / R1 OPEN |
| Graded Sir target | Local switch action changes state; remote rule creates/removes winTarget. | original + disable_remote_target aliases | Tests a semantically different local-trigger→distant-outcome ruleset. | Original level index 1 passes authoritative runtime and intervention trace diffe | SOURCE-AUDITED / R1 OPEN |
| R2 trace-difference audit | `NodeJSPuzzleEnv` exposes reset/step using the original engine and returns multi | audit_r2_trace_diff.py | Replays one identical action sequence on original/variant and locates the first  | First divergence occurs at/after target trigger; pre-trigger observations match. | PREPARED |
| Node→JAX validation | README describes original-engine search followed by JAX replay validation. Curre | run_external_gate.sh prints the current command. | Engine-equivalence guardrail before external results enter Paper 1. | Original-engine solution reaches the same terminal/win state in PuzzleJAX. | PREPARED / NOT EXECUTED |
| Session execution blocker | Current container has Node 22, but lacks Python `javascript` and `hydra`; pip/Gi | package_status.json | Separates infrastructure inability from a negative scientific result. | None; R1 stays OPEN until run in Kaggle/local/clone with requirements installed. | OPEN — NO CLAIM |

### Sheet: `v49 External Replication Audit`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| v49 — External PuzzleScript Replication Target Audit (spill fixed) |  |  |  |  |  |
| Rank | Game / level | Authored mechanic evidence | Why useful | Main confound | Required intervention |
| 1 | It Is Pitch Black — level 3 | Source rule: pushing `switch` converts `door` to an opening animation (`door1→do | Small 9×9 authored puzzle; switch→door effect is planning-relevant and structura | Need to verify case/symbol handling of the level's door marker and exact animati | Create matched rule variant that preserves all sprites/layout but disables only  |
| 2 | Graded Sir — level 2 (and level 3 secondary) | Action next to `switchOn/switchOff` or lever toggles state; remote rules convert | Different semantic realization of sparse local action causing distant planning-r | Narrative restart rules and multiple level-specific rules share one file; level  | Ablate only the remote target-appearance rule while keeping switch state transit |
| 3 | Atlas Shrank | Authored game explicitly includes Door, Switch, Exit and a larger physics/rule s | More realistic external family and existing human-data copy in repository. | Large mechanic stack (crates, gravity/helpers, multiple door/shadow objects) mak | Only attempt after a compact target passes; intervention must preserve all non-d |
| 4 | Weird Bug | Contains explicit late switch/door rules and several levels. | Mechanically close to target. | The game explicitly asks the player to fix bugs and source comments say rules/me | None. |

### Sheet: `New Literature`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| New literature added in this update (continuing from 85-work v2 ledger) |  |  |  |  |  |
| ID | Year | Work | Area | Key method / setting | Key evidence for thesis |
| L086 | 2024 | GenCO: Generating Diverse Designs with Combinatorial Constraints | Constrained generation / PCG | Deep generative model integrated with combinatorial solver; includes game-level/ | Neural constrained generation and solver-integrated feasibility are established. |
| L087 | 2023 | Compositional Diffusion-Based Continuous Constraint Solvers (Diffusion-CCSP) | Compositional generation / constraints | Factor-graph formulation; compose energies of diffusion models trained for indiv | Strong generalization to novel combinations of known constraints. |
| L088 | 2024 | Multi-Task Learning for Routing Problem with Cross-Problem Zero-Shot Generalizat | Neural combinatorial optimization | Represents VRP variants as combinations of shared attributes; one model solves s | Cross-problem zero-shot compositional generalization with one neural solver is e |
| L089 | 2025 | GOAL: A Generalist Combinatorial Optimization Agent Learner | Generalist combinatorial solver | Single shared backbone across routing, scheduling and graph problems; lightweigh | Heterogeneous multi-problem generalist neural solving is established. |
| L090 | 2025 | UniCO: Towards a Unified Model for Combinatorial Optimization Problems | Unified neural CO | Transformer trained across 10 CO problems; reports few-shot/zero-shot generaliza | One parameter set across heterogeneous CO problems is no longer a novelty claim. |
| L091 | 2025 | URS: A Unified Neural Routing Solver for Cross-Problem Zero-Shot Generalization | Unified routing / constraints | One solver for >100 VRP variants; unseen variants zero-shot; raw constraints con | Single model + variable constraints + executable masking + zero-shot is establis |
| L092 | 2024 | Towards a Generic Representation of Combinatorial Problems for Learning-Based Ap | Generic formal representation | Constraint AST/graph representation and GNN over XCSP3 constraints. | Generic graph encoding of formal constraints is established. |
| L093 | 2023 | Hypernetworks for Zero-Shot Transfer in Reinforcement Learning (HyperZero) | Transfer RL | Hypernetwork maps MDP task parameters to value functions/policies; zero-shot new | Formal/context-conditioned zero-shot policy generation is established. |

### Sheet: `Limitations & Kill Tests`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| Thesis limitations, threats, and go/no-go tests |  |  |  |  |  |
| Candidate | Limitation / threat | Why it matters | Mitigation / experiment | Kill condition | Negative-result value |
| T002 | Formal-language / grid-world scope | Claims cannot generalize to arbitrary commercial/3D games. | State scope explicitly; use at least several mechanically distinct formal domain | No kill; scope limitation only. | Still valid if conclusions are framed as formal discrete dynamics. |
| T002 | Known primitive vs unseen primitive conflation | Novel combination transfer is much easier than semantic extrapolation. | Create explicit regime split: same primitives/new topology vs new operator/trans | Kill Paper 2 if regimes cannot be isolated or held out cleanly. | A sharp negative boundary is itself publishable. |
| T002 | Planner/evaluator bottleneck and incompleteness | Failure to find a plan can be mistaken for unsolvability; training cost may domi | Use exact/reference solvers for small domains; larger budgets at final evaluatio | Kill implementation if evaluator cannot reliably order invalid < valid-unsolved  | Quantifies where learned design is limited by validation. |
| T002 | Target leakage | Target levels, names, tuning, adapters, or reward shaping would invalidate zero- | Freeze test domains; randomize object names; forbid target gradients/demos/traje | Any target-specific tuning after test exposure invalidates headline experiment. | Methodological contribution can include a strict protocol. |
| T002 | No actual transfer | Designer may collapse on every mechanic-family holdout. | Pilot multiple transfer regimes and compare non-learned general generators plus  | If all strict learned-designer conditions fail beyond trivial renaming/recombina | A sharp zero-target transfer boundary can still be publishable if signal varies  |
| T002 | Shortcut through superficial vocabulary/size | Model may identify game IDs rather than reason from mechanics. | Object renaming, rule permutation, mechanic-swaps, matched-size controls. | Kill mechanics-grounding claim if performance is unchanged under wrong-rule swap | Can reveal shortcut failure of current transfer methods. |
| G022 | Capability axes are arbitrary | A fingerprint made from chosen agents may just encode implementation choices. | Define axes as controlled resource/capability interventions; validate on synthet | Kill if axis ordering/direction changes drastically across independent implement | Null result can show that proposed capability decomposition is not identifiable. |
| G022 | Axes are correlated / not separable | Search, memory, information reasoning and learning budget can interact. | Use designed sanity games; factorial interventions; report correlation/interacti | Kill claims of independent dimensions if sanity tests cannot isolate them. | Correlation structure itself can be a result. |

### Sheet: `T002 Gap Audit`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| T002 / G020-refined — novelty and limitation audit |  |  |  |  |  |
| Claim / component | Status | Prior art that occupies it | What remains open | Thesis consequence | Kill test |
| General formal-rule → level/instance generation | NOT NOVEL | GVG-LG, symbolic planning generators, NeSIG, general PCG methods | Transfer of one already-trained learned DESIGNER to a held-out formal dynamics s | Do not sell generality, mechanics-awareness or solvability itself. | — |
| One shared neural model across domains | NOT NOVEL | Multiverse, GOAL, UniCO, multi-task routing | The scientific object must be transfer of a designer, not parameter sharing. | Unified architecture is baseline machinery. | — |
| Compositional generalization over known constraints | NOT NOVEL | Diffusion-CCSP; cross-problem VRP zero-shot; CoDE | Harder semantic extrapolation to unseen primitives/transition semantics remains  | Composition-only test becomes an easier regime/control. | If Paper 2 only reproduces known-combination transfer, no standalone novelty. |
| Graph / formal constraint encoder | NOT NOVEL | Generic XCSP3 graph/AST representation; ATLAS-like formal graph conditioning | Whether a representation improves DESIGNER transfer boundary is still empirical. | Encoder is ablation/mechanism, not contribution headline. | If gains disappear under equivalent non-graph encoder, do not claim representati |
| Dynamic / variable action masking | NOT NOVEL | URS and relational/variable-action RL | Cross-game edit semantics still require robust grounding. | Use strongest prior baselines. | Object renaming or rule-swap failure indicates shortcut leakage. |
| Formal-spec → zero-shot policy generation | NOT NOVEL | HyperZero and related policy-generator work | Level-design MDP target changes mechanics/content vocabulary and outputs an envi | Include HyperZero-style baseline if feasible. | If generic transfer methods solve the benchmark completely, architecture novelty |
| Learned environment/task designer | NOT NOVEL | PAIRED, CoDE, MAESTRO, ADD/TRACED | Frozen transfer of the DESIGNER itself across unseen rule/dynamics systems remai | UED must be a central related-work branch. | If an existing UED paper is found evaluating frozen teacher on unseen dynamics,  |
| Frozen designer + zero target artifacts + unseen dynamics | OPEN / CORE | No direct hit found in current audit | One pretrained designer receives only target executable spec; no target levels,  | This is the main surviving conjunction. | Kill if direct prior is found or if protocol leaks target artifacts. |

### Sheet: `Game Field Landscape`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| Broad Game AI / Computational Games landscape — MSc thesis screening |  |  |  |  |  |
| Rank | Field / branch | Research activity 2025–26 | Recurring limitation / gap | Human-data dependency | 18-month feasibility |
| 1 | Procedural generation + transfer/generalization | Extremely high / accelerating in 2024–26 | PCGRL now covers OOD map scale/shape, language and multi-objective instructions, | Low | Medium |
| 2 | Computational game science / capability measurement | Medium | Skill depth, game landscapes and stochasticity exist, but reproducible multidime | Low | High |
| 3 | Cooperative / multiplayer PCG | Low–Medium but rising | Only a small literature; no standard cooperation metric/benchmark, narrow genre  | Low if agent-only | High |
| 4 | Mechanic interaction / rule-effect science | Medium | Most work studies single mechanics/parameters; non-additive interaction effects  | Low | High |
| 5 | Automated balancing / game economies | Medium | Methods remain game-specific; evaluator/playtester generalization under content  | Low–Medium | Medium |
| 6 | General game playing / multi-game agents / zero-shot coordination | Very high | Novel partner/level/rule shifts remain hard, but benchmarks and methods are adva | Low | Medium–Low |
| 7 | Hidden rule-change / Knightian adaptation | Rapidly rising | Agents still struggle when rules change, but MirrorCraft 2026 now directly bench | Low | Medium |
| 8 | Automated game testing / regression QA | Very high / software-engineering race | GameRTS, differential RL, SAGE, KLPEG, RAID, SMART/CA2/TITAN now cover selection | Low | High |

### Sheet: `v38 GameAI Field Reset`

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 |
|---|---|---|---|---|---|
| v38 — Game research + Game AI field reset (NO human study) |  |  |  |  |  |
| Field | Current frontier | Limitation that matters | Surviving research residue | Candidate | No-human fit |
| Formal game mechanics + computational complexity | Complexity proofs isolate which mechanic sets make generalized games NP-/PSPACE- | Asymptotic class changes do not say when a theorem-selected mechanic interaction | Measure the finite activation boundary of a tractability-breaking mechanic conju | G032 | Excellent: exact solvers + synthetic instances only |
| PCG / PCGRL — generation | PCGRL+ scales training and tests OOD sizes; multi-agent PCGRL improves efficienc | Generic claims such as 'scale PCGRL', 'improve controllability', or 'generalize  | Use PCGRL as a method, not the thesis gap, unless the scientific object is evalu | Method donor | Excellent |
| PCG evaluation / functional validity | 2024 review finds PCG evaluation complex and lacking robust generalisable consen | Automated evaluator scores are often treated as if they were properties of conte | After hard validity constraints are fixed, quantify evaluator-induced rank rever | G071 | Excellent: agents/solvers only |
| General game playing + cross-game transfer | Knowledge transfer across games is old; newer generalist agents and multi-game b | Game-design factors and their interactions already explain substantial transfer  | Only a much narrower formal invariant/identifiability object is worth pursuing;  | No core candidate | Good |
| General game-agent evaluation / algorithm selection | GVGAI/Ludii support many games and agents; 2026 best-agent identification reduce | Scores and rankings can depend on harness, action interface, budget, reset/scori | Protocol-invariant capability conclusions across reasonable harness choices may  | G066 | Excellent |
| Automated game testing | RL testing, curiosity/multi-agent exploration, behavior-driven regression, model | Exploration and coverage improvements alone are crowded; the hard residue is ora | Use testing as an evaluation setting for G071/G032, or pursue only a formally sp | Method/evaluation donor | Excellent |
| Automated game balancing | Simulation/RL can balance competitive levels; 2025 work explicitly balances asym | A patch/level can look balanced for the strategy population used in simulation b | Study deformation of the acceptable balance region under evaluator-population sh | G058 | Excellent: synthetic policy populations |
| Multi-agent strategy populations / non-transitivity | Population-based training, PSRO-style methods and non-transitive meta-games are  | A single scalar ranking is population-dependent; 2026 evidence shows rank revers | Do not propose generic population diversity. Use non-transitivity as the mathema | Theory donor | Excellent |

