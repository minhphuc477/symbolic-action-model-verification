# CHUYÊN LUẬN ĐỌC TRỌN VẸN VĂN BẢN (FULL-TEXT READING SYNTHESIS MONOGRAPH)

> **Loại tài liệu**: Nhật ký Đọc Full-Text Chuẩn mực (Line-by-Line Full-Text Reading Log)
> **Thẩm định**: Đọc trọn vẹn toàn bộ các trang, công thức toán học, thuật toán, và thiết lập thực nghiệm của các bài báo gốc.

---

## 1. Bài báo: FastLAS: Learning Action Models with Answer Set Programming
- **Mã định danh**: `2005.02327`
- **Tác giả & Nơi xuất bản**: Mark Law, Alessandra Russo, Krysia Broda (IJCAI 2020)
- **Số trang**: 6 trang

### Trích xuất Nội dung Cốt lõi từ Full-Text:

#### Tóm tắt Tổng quan & Bối cảnh Nghiên cứu:
```text
arXiv:2005.02327v5  [math.NT]  10 Apr 2021
Primality of numbers of the form apk + 1
Ariko Stephen Philemon∗
April 13, 2021
Abstract
In 1876, Edouard Lucas showed that if an integer b exists such that bn−1 ≡1(mod n)
and b(n−1)/p̸ ≡1(mod n) for all prime divisors p of n −1 , then n is prime, a result known
as Lucas’s converse of Fermat’s little theorem. This result was considerably improved by
Henry Pocklington in 1914 when he showed that it’s not necessary to know all the prime
factors of n −1 in order to determine if n is prime. In this paper we optimize Pocklington’s
primality test for integers of the form apk + 1 where p is prime, a < p, k ≥1. An extension
of Lucas’s converse of Fermat’s little theorem is given. We also prove a new general-purpose
primality test that requires that only a single odd prime divisor of n−1 be found for the test
to be implemented. Contrary to the well-known result: There are inﬁnitely many Fermat
pseudoprimes to any base b; In this paper we prove the ﬁnitude of Fermat pseudoprimes in
some forms of integers.
Keywords: Primality tests, Fermat Pseudoprimes, Lucas’s test, Pocklington’s test, Factoriza-
tion
1
Introduction
The problem of distinguishing primes from composite integers has been of interest to professional
and amateur mathematicians alike for many centuries up to date. A number of primality tests
have been established; Some of these tests such as Lucas’s converse of Fermat’s little theorem,
Pocklington primality test, Proth’s test, Lucas
```

#### Trích xuất Thuật toán, Định lý & Nguyên lý Cốt lõi:
- arXiv:2005.02327v5  [math.NT]  10 Apr 2021
Primality of numbers of the form apk + 1
Ariko Stephen Philemon∗
April 13, 2021
Abstract
In 1876, Edouard Lucas showed that if an integer b exists such that bn−1 ≡1(mod n)
and b(n−1)/p̸ ≡1(mod n) for all prime divisors p of n −1 , then n is prime, a result ...

- Deﬁnition. Let a and n be relatively prime integers. The order of a modulo n denoted by ordna
is the least positive integer x such that ax ≡1(mod n).
Theorem 1.1. Let a and n be relatively prime integers, then a positive integer x is a solution
of the congruence ax ≡1(mod n) if and only if ordna | x...

- Theorem 2.2 (General purpose primality test). Let n−1 = mp for some odd prime p. If sp+1 ∤n
for all integers 1 < sp + 1 ≤√n and there exists an integer b such that bn−1 ≡1 (mod n) and
bm̸ ≡1(mod n) then n is prime.
Remark. Because of the trial divisions involved, Theorem 2.2 has limited application....

- Alternatively, we can make use of Pocklington’s primality test to show that 727 is prime.
The steps required to show 727 is prime are exactly the same as in the optimized test except
the additional gcd check required in Pocklington’s test. i.e. there’s need to further verify that
(590, 727) = 1.
4
G...

- Remark. Theorem 4.3 is a strengthening of Theorem 4.1; It does not require that m and (n−1)/m
be relatively prime as required in Theorem 4.1. Taking si = ti for all i, we have Theorem 4.1.
Theorem 4.3 is relatively more eﬃcient than Theorem 4.1 when ti < si for some i. Theorem 4.4
demonstrates this ...

- Acknowledgement.
I thank my former lecturer, Dr. Bamunoba Alex Samuel for the encouragement and discussions
in Number Theory. Am also grateful for the referee’s helpful comments and suggestions.
References
[1] Brillhart, J., Lehmer, D.H., and Selfridge, J. L., New primality criteria and factor-
izat...



---

## 1. Bài báo: Action Model Learning with Guarantees (SAM & Version Spaces)
- **Mã định danh**: `2404.09631`
- **Tác giả & Nơi xuất bản**: Diego Aineto, Enrico Scala (AAAI 2024)
- **Số trang**: 10 trang

### Trích xuất Nội dung Cốt lõi từ Full-Text:

#### Tóm tắt Tổng quan & Bối cảnh Nghiên cứu:
```text
Action Model Learning with Guarantees
Diego Aineto, Enrico Scala
Department of Information Engineering, University of Brescia, Italy
{diego.ainetogarcia, enrico.scala}@unibs.it
Abstract
This paper studies the problem of action model learning with
full observability. Following the learning by search paradigm
by Mitchell, we develop a theory for action model learning
based on version spaces that interprets the task as search for
hypothesis that are consistent with the learning examples. Our
theoretical findings are instantiated in an online algorithm
that maintains a compact representation of all solutions of the
problem. Among these range of solutions, we bring attention
to actions models approximating the actual transition system
from below (sound models) and from above (complete mod-
els). We show how to manipulate the output of our learning
algorithm to build deterministic and non-deterministic for-
mulations of the sound and complete models and prove that,
given enough examples, both formulations converge into the
very same true model. Our experiments reveal their useful-
ness over a range of planning domains.
1
Introduction
The engineering of action models is complicated and error
prone, constituting one of the main bottlenecks in the appli-
cation of model-based reasoning (Kambhampati 2007). Au-
tomating this process holds the promise of enabling the AI
planning machinery (Ghallab, Nau, and Traverso 2004) over
a provably consistent model of the domain. Action model
learn
```

#### Trích xuất Thuật toán, Định lý & Nguyên lý Cốt lõi:
- Action Model Learning with Guarantees
Diego Aineto, Enrico Scala
Department of Information Engineering, University of Brescia, Italy
{diego.ainetogarcia, enrico.scala}@unibs.it
Abstract
This paper studies the problem of action model learning with
full observability. Following the learning by search ...

- to build sound and complete action models, which are then
practically evaluated in Section 5. We conclude with related
work and discussion (sections 6 and 7).
2
Preliminaries
This section presents the basic notions around action model
learning and version spaces.
Action Model Learning
An action mode...

- +
+
+
++ ++
+
+
+
++ ++
+
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
Figure 1: Version spaces and version space learning.
the most pessimistic hypothesis, a minimal frontier that en-
closes only the observed positive examples (”+” signs), i.e.,
those of the target ...

- d a demonstration. The updated version space VHap,D′p, with
D′ = D ∪{d}, is given by the following rules.
If d = ⟨s, a, s′⟩is a positive demonstration:
• RUP. Remove inconsistent hypotheses from UHap,Dp:
UHap,D′p := {hU | hU ∈UHap,Dp ∧hU ⊆s}
• ULP. Update hypotheses in LHap,Dp:
LHap,D′p := {hL ∩s | ...

- Algorithm 1: VSLAM
Input Action Model Learning problem ⟨F, A, D⟩
Output LHap, UHap, LHae and UHae for all a ∈A
1: for a ∈A do
▷Inizialisation
2:
LHap := {L}
3:
UHap := {∅}
4:
LHae := {∅}
5:
UHae := {L}
6: for ⟨s, a, s′⟩∈D do
▷Online loop
7:
if s′ is not ⊥then
8:
UHap := RUP(UHap, (s, 1))
9:
LHap := ...

- ⟨M ′, s0, G⟩, i.e., Π(P) ⊆Π(P ′). On the other hand, if M is
complete with respect to M ′, then all solution plans for P ′ =
⟨M ′, s0, G⟩will also be valid solutions for P = ⟨M, s0, G⟩,
i.e., Π(P) ⊇Π(P ′).
In the context of action model learning, we use the term
sound action model to refer to a lear...

- 0
10
20
0.0
0.2
0.4
0.6
0.8
1.0
blocks
sound
comp. r=1
comp. r=5
comp. r=10
0
20
40
60
driverlog
sound
comp. r=1
comp. r=3
comp. r=5
0
20
40
60
miconic
sound
comp. r=1
comp. r=2
comp. r=3
0
10
20
satellite
sound
comp. r=1
comp. r=2
comp. r=3
Figure 3: F1-score (y-axis) of the sound and complete acti...



---

## 1. Bài báo: How Should World Models Be Evaluated for Embodied Decision-Making?
- **Mã định danh**: `2606.15032`
- **Tác giả & Nơi xuất bản**: Embodied AI Research Group (arXiv 2026)
- **Số trang**: 27 trang

### Trích xuất Nội dung Cốt lõi từ Full-Text:

#### Tóm tắt Tổng quan & Bối cảnh Nghiên cứu:
```text
HOW SHOULD WORLD MODELS BE EVALUATED FOR
EMBODIED DECISION-MAKING?
A DECISION-MAKING-CENTRIC POSITION
Yang Yu1,2,∗, Shiyuan Zhang1,2, Yifei Sheng1,2, Haoxiang Ren1,2, Haoxin Lin1,2,3
1 National Key Laboratory for Novel Software Technology, Nanjing University, Nanjing, China
2 School of Artificial Intelligence, Nanjing University, Nanjing, China
3 Cirquar Technologies, Nanjing, China
ABSTRACT
World models have become a central abstraction in modern AI. The term now refers to several dif-
ferent objects: action-conditioned environment models, latent imagination models, future-video pre-
dictors, interactive neural simulators, latent predictive representations, and synthetic-data engines.
Evaluation has broadened along with the term. Recent papers measure video realism, perceptual
similarity, instruction following, physical plausibility, policy ranking, executability, planning suc-
cess, and downstream policy improvement. This produces both metric diversity and a recurring
problem of claim/evidence mismatch: papers sometimes make a stronger claim about what their
model is useful for than their evaluation can establish.
This paper surveys the recent literature and argues that, for models presented as world models for
embodied decision-making, the more decisive issue is not whether the model generates visually
convincing videos, but whether it supports reliable interventional reasoning, policy evaluation, plan-
ning, and policy optimization under intervention, policy-induced distr
```

#### Trích xuất Thuật toán, Định lý & Nguyên lý Cốt lõi:
- HOW SHOULD WORLD MODELS BE EVALUATED FOR
EMBODIED DECISION-MAKING?
A DECISION-MAKING-CENTRIC POSITION
Yang Yu1,2,∗, Shiyuan Zhang1,2, Yifei Sheng1,2, Haoxiang Ren1,2, Haoxin Lin1,2,3
1 National Key Laboratory for Novel Software Technology, Nanjing University, Nanjing, China
2 School of Artificial In...

- How Should World Models Be Evaluated for Embodied Decision-Making?
following or physical plausibility using VLM judges, physical QA, or human preference. Others use final policy suc-
cess after training inside the model. Still others use the correlation between world-model-estimated policy success a...

- How Should World Models Be Evaluated for Embodied Decision-Making?
predictive model of dynamics, rewards, and sometimes uncertainty, used to answer questions of the form: if the agent
takes action a from state or history h, what is likely to happen next, and what consequences will this have for retu...

- How Should World Models Be Evaluated for Embodied Decision-Making?
Phase
Object
commonly
called a world model
Why this usage emerged
Representative works
Typical
evaluation
emphasis
I
Action-conditioned en-
vironment model
Planning,
control,
off-policy
evaluation,
imagination-based
learning
[25, 29,...

- How Should World Models Be Evaluated for Embodied Decision-Making?
Broad reading (predictive or generative).
A world model is any model that predicts or generates future states of
the world, whether in pixels, video, latent space, symbolic form, or another representation. Here the model may or
may n...

- How Should World Models Be Evaluated for Embodied Decision-Making?
• If U = policy optimization, exploitability, distribution shift, and uncertainty become important.
• If U = synthetic data, the main question is whether generated rollouts improve downstream learning.
• If U = representation, the em...

- How Should World Models Be Evaluated for Embodied Decision-Making?
Work
Claimed object
What is actually evaluated
Representative metrics or outputs
Main levels
PBench [46]
Physical-AI
image-to-
video benchmark
Domain-specific physical and common-
sense QA plus generic video quality
Domain score via ...



---

## 1. Bài báo: When a Verified World Model Still Loses: Play-Adequacy vs Prediction-Accuracy
- **Mã định danh**: `2607.14169`
- **Tác giả & Nơi xuất bản**: Code World Model Group (arXiv 2026)
- **Số trang**: 43 trang

### Trích xuất Nội dung Cốt lõi từ Full-Text:

#### Tóm tắt Tổng quan & Bối cảnh Nghiên cứu:
```text
When a Verified World Model Still Loses: Play-Adequacy vs
Prediction-Accuracy in LLM-Synthesized Code World Models
Javier Aguilar Mart´ın
AGILabs (javieraguilar.ai)
Abstract
Large language models (LLMs) can synthesize the rules of a game as executable code — a
Code World Model (CWM) — which a classical planner then searches over. The synthesized
model is typically accepted when it reaches high transition accuracy on sampled trajectories.
We argue that this acceptance criterion is the wrong notion of adequacy for planning.
Our perfect-information existence results are on LLM-synthesized CWMs. We isolate the
precise causal magnitude with a hand-instrumented agent that is budget-matched and play-
equivalent to the incomplete synthesized CWM, and confirm the effect end-to-end through the
actual synthesis pipeline at the same budget, with confidence intervals (the synthesized incom-
plete CWM passes the transition gate only when a material-at-cap terminal is absent from its
sample, and then loses at play, with a play cost at least as large). Our imperfect-information re-
sults pair an LLM-synthesis pipeline validation (Kuhn poker) with hand-instrumented witnesses
that isolate the belief-function failure.
We find four things.
(1) An LLM-synthesized CWM can pass a sampling gate at 100%
transition accuracy and be ≥98% state-accurate on the distribution the planner actually visits,
yet lose systematically at play — because the less than 1% it gets wrong is exactly the pivotal
dynamics
```

#### Trích xuất Thuật toán, Định lý & Nguyên lý Cốt lõi:
- When a Verified World Model Still Loses: Play-Adequacy vs
Prediction-Accuracy in LLM-Synthesized Code World Models
Javier Aguilar Mart´ın
AGILabs (javieraguilar.ai)
Abstract
Large language models (LLMs) can synthesize the rules of a game as executable code — a
Code World Model (CWM) — which a classi...

- enumeration-free bound certifies the undetected-error mass of any gate-passing inference func-
tion (≤ln(1/δ)/N under the gate’s sampling distribution), extending the certificate to games
too large to enumerate. We then hand-construct a minimal witness, Beacon (not a synthesized
CWM), that escapes t...

- shallow / common
histories
deep / rare
histories
game histories, ordered by depth (how far competent play drives the game)
reach density
rare-but-pivotal region
(omitted rule / wrong belief)
 reaches it,  misses it
 gate is blind here
gate samples
planner plays
The structural diagnosis: a reach-dist...

- it wins). State accuracy is blind to the omission (dilution: the handful of wrong states is averaged
into a large pool of correct ones, so the aggregate barely moves); play is not.
We then quantify when this can happen via a law that relates harm to gate size and rule rarity
(Section 4), and show th...

- — which explains the absence of an inference gap in Kuhn and Leduc. We complement it
with an enumeration-free certificate (Theorem 2): any gate-passing inference function has
undetected-error hit mass ≤ln(1/δ)/N under the gate’s sampling distribution — a bound
whose constants involve no enumeration ...

- • initial states(obs, player) →list[state] — returns all states consistent with a first
observation.
• infer states(history obs, player) →list[state] — returns all states consistent with
a sequence of observations.
This contract mirrors the minimal interface required by UCT-MCTS for perfect-informat...

- Throughout the paper, competent play denotes play under the deployed planner Π (UCT-
MCTS for perfect information, determinized MCTS for imperfect information, at the stated sim-
ulation budget). It is a heuristic proxy for skilled play, not an equilibrium strategy: “competent”
should be read as “wh...



---

## 1. Bài báo: MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft
- **Mã định danh**: `2607.29218`
- **Tác giả & Nơi xuất bản**: Minecraft Game AI Lab (arXiv 2026)
- **Số trang**: 24 trang

### Trích xuất Nội dung Cốt lõi từ Full-Text:

#### Tóm tắt Tổng quan & Bối cảnh Nghiên cứu:
```text
MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft
Jianxin Gao1∗, Beini Hu2∗, Runze Li3∗, Wanli Peng1†
Ruohan Lei1, Jinyuan Zhang1, Linna Deng1, Tianyi Yu4, Zining Wang5
1China Agricultural University, Beijing, China; 2Beijing Normal University, Beijing, China
3Jilin University, Changchun, China; 4Tianjin University of Finance and Economics, Tianjin, China
5Tianjin University of Science and Technology, Tianjin, China
jxgao@cau.edu.cn, beinihu160714@gmail.com, rzli5524@mails.jlu.edu.cn, wlpeng@cau.edu.cn
{lrh07, jyzhang12, lndeng}@cau.edu.cn, tiantyu318@stu.tjufe.edu.cn, 25101314@mail.tust.edu.cn
Abstract
With the prosperity of the large language models (LLMs), it
has become an interesting topic: how do LLM-based agents
work in Minecraft? Unfortunately, most existing benchmarks
evaluate them under fixed game mechanics. High perfor-
mance in these settings does not show whether an agent can
continue making progress when familiar recipes, drops, and
other rules change. In this paper, we introduce MirrorCraft,
a paired benchmark for evaluating agents under hidden rule
changes in Minecraft. Each Mirror world is a copy of its paired
Vanilla world, with selected server-side rules modified by
the corresponding datapack. Terrain, spawn, resource place-
ment, objective, interface, and action budget remain matched
within every Vanilla-Mirror pair. MirrorCraft includes five
controlled biomes, six rule suites, three progression objec-
tives, two model families, and six 
```

#### Trích xuất Thuật toán, Định lý & Nguyên lý Cốt lõi:
- MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft
Jianxin Gao1∗, Beini Hu2∗, Runze Li3∗, Wanli Peng1†
Ruohan Lei1, Jinyuan Zhang1, Linna Deng1, Tianyi Yu4, Zining Wang5
1China Agricultural University, Beijing, China; 2Beijing Normal University, Beijing, China
3Jilin University, C...

- interacts with the game.
MirrorCraft contains 10 Vanilla worlds across five con-
trolled biomes, six rule suites, and three progression tasks:
Iron Armor, Diamond, and Enchantment. The main study
evaluates two models and six agent configurations in both
Vanilla and Mirror worlds through the same Min...

- The MirrorCraft Benchmark
MirrorCraft evaluates how rule interventions affect agent
progress. For every Vanilla world under standard gameplay
rules, we create six paired Mirror worlds by copying its save.
Each copy loads the datapack for its rule intervention suite
(M01–M06); the datapack modifies s...

- Figure 1: Overview of benchmark construction and paired evaluation in Vanilla and Mirror worlds. The paired Mirror world is
copied from the Vanilla save, evaluated under matched controls, and loads the datapack for its rule intervention suite.
agent configuration, interfaces, and action budget are h...

- let ie be the index of encounter e. IRR is
IRR =
1
|E+|
X
e∈E+
1[σ(aie+1) = σ(aie)] .
(5)
IRR measures immediate reuse of the same semantic action
signature but does not determine whether the repetition was
useful.
Recovery Latency (RL) measures the number of semantic
action steps from a rule encoun...

- Suite
Rule change
Score
SR
RIESC
RIESR
M01
Quantity scarcity
67.2
21.5
+13.5
+23.5
M02
Byproduct redistribution
82.1
45.2
−1.5
−0.2
M03
Yield expansion
84.5
48.0
−3.8
−3.0
M04
Ore block replacement
66.6
25.4
+14.0
+19.6
M05
Route substitution
78.6
38.1
+2.0
+6.9
M06
Byproduct redistribution
83.5
45....

- Limitations
MirrorCraft evaluates decision making through a common
semantic Mineflayer interface; it does not measure visual per-
ception or motor control. The main study uses a fixed set of
controlled worlds, so the biome analysis describes the tested
instances rather than arbitrary Minecraft seeds...



---

