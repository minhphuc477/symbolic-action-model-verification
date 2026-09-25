# Tổng Quan Nghiên Cứu Văn Hiệt 5 Năm (2021 – 2026) Trong Sổ Ký Lục Nghiên Cứu Excel

> **Tập tin nguồn**: `ai_games_research_ledger_2026-09-09_v50_external_runtime_harness.xlsx` (Sheet `New Literature`)  
> **Tổng số công trình (2021–2026)**: **280 bài báo / công trình nghiên cứu**  
> **Thời gian thực hiện**: Cập nhật đến tháng 9/2026.

---

## 1. Thống Kế Tổng Quan Văn Hiệt 5 Năm

| Năm | Số lượng công trình | Tỷ lệ | Các Chủ đề & Hội nghị Tiêu biểu |
| :---: | :---: | :---: | :--- |
| **2026** | **118 bài** | **42.1%** | ICLR, NeurIPS, AAAI, IJCAI, USENIX Security, IEEE ToG, GECCO, Annual Reviews |
| **2025** | **84 bài** | **30.0%** | NeurIPS, KDD, ICAPS, Applied Psychological Measurement, KCI, arXiv preprints |
| **2024** | **42 bài** | **15.0%** | ICAPS, ICLR, AAAI, Reinforcement Learning Journal, IEEE CEC |
| **2023** | **18 bài** | **6.4%** | NDSS, JAIR, NeurIPS, ICML |
| **2022** | **11 bài** | **3.9%** | CP (LIPIcs), IJCAI, NeurIPS |
| **2021** | **7 bài** | **2.5%** | FDG, AISTATS, NeurIPS |

---

## 2. 6 Trụ Cột Nghiên Cứu Chính (2021–2026)

### A. World Models, Action Model Learning & Causal Reasoning (85 Bài báo)
Tập trung vào việc học mô hình động lực học của môi trường, suy luận nhân quả, và phân tách giữa độ chính xác dự đoán bề nổi (*Prediction Accuracy*) và tính thỏa đáng khi hoạch định (*Planning Adequacy*).

- **[L446] Aguilar Martín (2026)**: *When a Verified World Model Still Loses: Play-Adequacy vs Prediction-Accuracy in LLM-Synthesized Code World Models* (arXiv:2607.14169).
  - *Phương pháp*: Đánh giá CWMs do LLM tổng hợp trên các game logic rời rạc.
  - *Phát hiện*: Mô hình đạt 100% Transition Accuracy vẫn thua 100% ván đấu do bỏ sót pivotal rules. Chi phí sụt giảm $B = 0.091$.
- **[L447] Gao et al. (2026)**: *MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft* (arXiv:2607.29218).
  - *Phương pháp*: Đánh giá agent dưới biến thể luật cặp server-side (Vanilla vs Mirror).
  - *Phát hiện*: Agent suy sụp hoàn toàn khi luật ẩn thay đổi; văn bản mô tả luật mang lại cải thiện rất nhỏ.
- **[L445] Multiverse Mechanica (2026)**: *A Testbed for Learning Game Mechanics via Counterfactual Worlds* (ICLR 2026).
  - *Phương pháp*: Tạo môi trường counterfactual worlds để kiểm thử khả năng học game mechanics.
- **[L441] Safe Learning of PDDL Domains with Conditional Effects (2024)**: *ICAPS 2024* (AAAI OJS).
  - *Phương pháp*: Học an toàn các miền PDDL có hiệu ứng điều kiện.
- **[L442] Deng et al. (2026)**: *Stochastic Safe Action Model Learning* (COLT 2026 / PMLR).
  - *Phương pháp*: Học mô hình hành động an toàn trong môi trường ngẫu nhiên.

---

### B. Procedural Content Generation (PCG) & Quality-Diversity (45 Bài báo)
Tập trung vào sinh màn chơi tự động, tối ưu đa mục tiêu và duy trì sự phong phú cơ chế game.

- **[L448] Mortar (2026)**: *Evolving Mechanics for Automatic Game Design* (GECCO 2026).
  - *Phương pháp*: Dùng thuật toán tiến hóa (Evolutionary Algorithms) để tự động sinh và tiến hóa cơ chế game.
- **[L452] Cooperative Coevolution QD (2024)**: *Sample-Efficient Quality-Diversity by Cooperative Coevolution* (ICLR 2024).
  - *Phương pháp*: Tăng hiệu quả mẫu cho Quality-Diversity bằng tiến hóa hợp tác.
- **[L451] Surrogate-Assisted Illumination (2018/2022)**: *Evolutionary Computation*.
  - *Phương pháp*: Dùng mô hình thay thế (Surrogate) để tăng tốc tìm kiếm MAP-Elites.

---

### C. General Game Playing (GGP), Benchmarks & Agent Reliability (52 Bài báo)
Tập trung vào việc tạo bộ benchmark chuẩn mực và đánh giá tính tin cậy của AI Agent.

- **[L430] GameWorld (2026)**: *A Dynamic Benchmark for Generalist Agents in Interactive Game Environments* (arXiv 2026).
  - *Phương pháp*: Benchmark động đánh giá Generalist Agents trên các môi trường tương tác.
- **[L431] Best Practices for Agentic Benchmarks (2025)**: *Establishing Best Practices for Building Rigorous Agentic Benchmarks* (arXiv 2025).
  - *Phương pháp*: Đưa ra quy chuẩn phương pháp luận xây dựng benchmark agentic nghiêm ngặt.
- **[L432] OpenApps (2025)**: *Simulating Environment Variations to Measure UI-Agent Reliability* (arXiv 2025).
  - *Phương pháp*: Mô phỏng biến thể môi trường để đo độ tin cậy của UI agents.
- **[L453] PuzzleJAX (2025)**: *A Benchmark for Reasoning and Learning* (NeurIPS Workshop 2025 / arXiv).
  - *Phương pháp*: Tái tạo và tăng tốc song song các bài toán suy luận đố trí trên JAX.

---

### D. Anti-Cheat, Security & Anomaly Detection trong Games (32 Bài báo)
Tập trung vào bảo mật server-side, phát hiện gian lận và chống anomaly.

- **[L424] XGuardian (2026)**: *Towards Generalized, Explainable and More Effective Server-side Anti-cheat in First-Person Shooter Games* (USENIX Security 2026).
  - *Phương pháp*: Anti-cheat server-side giải thích được cho game FPS.
- **[L425] Anomaly Detection in Open World (2023)**: *Normality Shift Detection, Explanation, and Adaptation* (NDSS 2023).
  - *Phương pháp*: Phát hiện và thích ứng với dịch chuyển chuẩn hóa (Normality Shift) trong môi trường mở.

---

### E. Player Skill, Matchmaking & Game Economics (40 Bài báo)
Tập trung vào mô hình hóa kỹ năng người chơi, matchmaking và kinh tế game tự động.

- **[L415] Matchmaking Strategies for Maximizing Player Engagement (2026)**: *Management Science 2026*.
  - *Phương pháp*: Tối ưu chiến lược ghép trận nhằm tối đa hóa mức độ gắn kết của người chơi.
- **[L422] Empowering Economic Simulation for MMOGs (2025)**: *KDD 2025*.
  - *Phương pháp*: Mô phỏng nền kinh tế MMOG bằng Generative Agent-Based Modeling.
- **[L420] GEEvo (2024)**: *Game Economy Generation and Balancing with Evolutionary Algorithms* (IEEE CEC 2024).
  - *Phương pháp*: Sinh và cân bằng kinh tế game bằng thuật toán tiến hóa.
- **[L437] PandaSkill (2025)**: *Player Performance and Skill Rating in Esports: Application to League of Legends* (arXiv 2025).
  - *Phương pháp*: Đánh giá kỹ năng và hiệu năng người chơi trong LMHT.

---

### F. Dynamic Difficulty Adjustment (DDA) & Adaptive Game AI (26 Bài báo)
Tập trung vào điều chỉnh độ khó tự động và AI thích ứng.

- **[L426] Dynamic Difficulty Adjustment in Serious Games (2026)**: *Information 2026* (MDPI - Đã gắn cờ thay thế).
- **[L419] Reinforcement Learning-based Player-Adaptive DDA (2025)**: *JISPS 2025*.
- **[L429] Dynamic Difficulty Adjustment with Simplification Ability (2019/2021)**: *Procedural Computer Science*.

---

## 3. Tổng Kết Các Xu Hướng Đột Phá 2021–2026

1. **Chuyển từ Dự đoán Thụ động sang Xác minh Chủ động (*Active Search-Tree Verification*)**:
   Các công trình năm 2025–2026 (L446, L456, L457) đồng loạt chứng minh rằng việc đánh giá AI dựa trên các bộ dữ liệu trajectory thụ động là hoàn toàn không đủ. Ngành đang chuyển sang các cổng kiểm định chủ động trên cây tìm kiếm (*Active Verification Gates*).
2. **Sự trỗi dậy của Code World Models (CWMs)**:
   LLM không chỉ dự đoán vector trạng thái mà tổng hợp trực tiếp mã nguồn Python/JAX đại diện cho động lực học môi trường (L318, L446).
3. **Thử nghiệm Can thiệp Luật Cặp (*Paired Rule Interventions*)**:
   Thay vì đánh giá trên môi trường cố định, các benchmark 2026 (MirrorCraft L447, Multiverse Mechanica L445) áp dụng các can thiệp luật ẩn server-side để đo lường khả năng học động lực nhân quả thực sự.
