# Phân Tích Chuyên Sâu Từng Phân Ngành: Hạn Chế, Khoảng Trống & Điểm Giao Thoa (Cross-Disciplinary Intersections)

> **Mục tiêu**: Đánh giá định lượng & định tính mức độ tập trung của các hạn chế (limitations) và khoảng trống mở (open gaps) qua 7 phân ngành Game AI, đồng thời phân tích tiềm năng khoa học vượt trội tại các **điểm giao thoa (intersections)** giữa các phân ngành.

---

## I. MỨC ĐỘ TẬP TRUNG HẠN CHẾ & KHOẢNG TRỐNG THEO 7 PHÂN NGÀNH

```mermaid
quadrantChart
    title Mức Độ Tồn Đọng Khoảng Trống (Gaps) & Tác Động Khoa Học (Impact)
    x-axis Mức độ Đầy đủ của Lý thuyết & Công cụ hiện tại --> Mức độ Tồn đọng Khoảng trống cao
    y-axis Mức độ Tác động Khoa học khi Giải quyết --> Tác động Khoa học Cực cao (High Impact)
    quadrant-1 Khung Vàng Đột Phá (Primary Research Frontier)
    quadrant-2 Bài Toán Nền Tảng (Foundational Theory)
    quadrant-3 Phân Ngành Đã Bão Hòa (Saturated Domain)
    quadrant-4 Ứng Dụng Kỹ Thuật (Engineering Application)
    Subfield 1 Code World Models: [0.75, 0.88]
    Subfield 2 PCG-QD & UED: [0.65, 0.82]
    Subfield 3 Rule Interventions: [0.70, 0.85]
    Subfield 4 Verified-vs-Correct Gap: [0.90, 0.95]
    Subfield 5 Generalist Agents: [0.45, 0.70]
    Subfield 6 Causal RL & PAC Bounds: [0.80, 0.90]
    Subfield 7 Auto Game Design & Balance: [0.55, 0.65]
```

### 1. Phân Ngành 4: Verified-vs-Correct Gap & Planning Adequacy (Mức độ Gaps: 95% - Cao nhất)
* **Trạng thái**: Đây là **lỗ hổng nghiêm trọng nhất** của toàn bộ ngành AI hiện tại.
* **Hạn chế hiện hữu**:
  * Các bài báo hiện tại (Aguilar Martín ICLR 2026, `2607.14169`) chỉ mới phát hiện hiện tượng $A_{	ext{pred}} \ge 98\% \implies R_{	ext{play}} = 100\%$ trên các bài test tự tay sửa luật thủ công (hand-instrumented).
  * Chưa có khung lý thuyết nào đo lường được chi phí tìm kiếm (planning burden) đối ứng với chi phí học mô hình khi luật game bị can thiệp.
  * Các bài báo kiểm thử phần mềm (`2604.04047`, `2512.00560`) bị hạn chế trong môi trường closed-world.

### 2. Phân Ngành 1: Code World Models & Symbolic Dynamics (Mức độ Gaps: 88%)
* **Trạng thái**: Đang phát triển bùng nổ (Lehrach DeepMind 2025, OpenWorld Sept 2026, `2609.09163`).
* **Hạn chế hiện hữu**:
  * Mới chỉ chứng minh được độ chính xác rollout 100% trên các môi trường tĩnh hoặc template thế giới được viết thủ công.
  * Thiếu thuật toán tự động bóc tách và sửa đổi cây cú pháp AST (AST code patching) khi gặp biến đổi luật OOD.

### 3. Phân Ngành 3: Rule Interventions & Counterfactual Benchmarks (Mức độ Gaps: 85%)
* **Trạng thái**: Mới khởi động năm 2026 (MirrorCraft `2607.29218`, CausalGame ICML 2026 `2607.04293`).
* **Hạn chế hiện hữu**:
  * Các bộ benchmark can thiệp luật hiện tại (MirrorCraft JSON datapacks) hoàn toàn phụ thuộc vào việc tác giả tự tay viết thủ công từng kịch bản can thiệp.
  * Chưa kết hợp với các thuật toán tiến hóa (QD/UED) để tự động hóa việc sinh các kịch bản can thiệp luật.

### 4. Phân Ngành 6: Causal RL & Active PAC Exploration Bounds (Mức độ Gaps: 90%)
* **Trạng thái**: Lý thuyết vững chắc nhưng thiếu công cụ benchmark thực tế.
* **Hạn chế hiện hữu**:
  * Đồ thị nguyên nhân (Causal DAGs) chủ yếu được gán nhãn thủ công hoặc áp dụng trên các game bài đơn giản (Causal MTG `2605.06066`).
  * Chưa có kết nối giữa ranh giới mẫu PAC Bounds ($O(k \log(1/\delta))$) với việc mở rộng cây tìm kiếm (World-Time Compute).

---

## II. SỰ GIAO THOA GIỮA CÁC PHÂN NGÀNH (CROSS-DISCIPLINARY INTERSECTIONS)

Khoảng trống khoa học lớn nhất **KHÔNG nằm ở bản thân từng phân ngành riêng lẻ**, mà nằm ở **ĐIỂM GIAO THOA (INTERSECTION)** giữa 4 phân ngành cốt lõi:

```mermaid
colorScheme ocean
flowchart TD
    subgraph GIAO THOA ĐỘT PHÁ (THE NOVELTY FRONTIER)
        S1["Phân Ngành 1:
Code World Models"] 
        S2["Phân Ngành 2:
PCG-QD & UED"]
        S3["Phân Ngành 3:
Rule Interventions"]
        S4["Phân Ngành 4:
Verified-vs-Correct Gap"]
        S6["Phân Ngành 6:
Causal RL & PAC Bounds"]
    end
    
    S1 & S2 & S3 & S4 & S6 ==> CORE_GAP["ĐIỂM GIAO THOA ĐỘT PHÁ:
Khung Chẩn Đoán & Thích Ứng Causal Zero-Shot
(Automated QD Interventional Benchmark + Active Tree Probing)"]
```

### 1. Điểm Giao Thoa 1: Code World Models (S1) $	imes$ PCG-QD (S2) $	imes$ Rule Interventions (S3)
* **Thực trạng**: S1 tạo mô hình thế giới dạng code, S2 tạo bài test đa dạng, S3 tạo biến đổi luật.
* **Khoảng trống giao thoa**: Chưa ai kết hợp CMA-ME QD với Code Mutation để **tự động sinh ra lưu trữ bài test can thiệp luật (Interventional QD Archives)** dưới dạng mã nguồn thực thi.

### 2. Điểm Giao Thoa 2: Verified-vs-Correct Gap (S4) $	imes$ Active PAC Bounds (S6) $	imes$ Code World Models (S1)
* **Thực trạng**: S4 phát hiện lỗi bẫy kiểm định thụ động, S6 cung cấp lý thuyết khám phá nguyên nhân PAC Bounds, S1 cung cấp trình duyệt mô hình thế giới dạng code.
* **Khoảng trống giao thoa**: Sử dụng thuật toán **Active Search-Tree Frontier Probing** để chứng minh toán học và thực nghiệm rằng chi phí lấy mẫu giảm từ $O(|S| \cdot |A|^d)$ xuống $O(k \log(1/\delta))$, triệt tiêu 100% Verified-vs-Correct Gap.

### 3. Điểm Giao Thoa 3: CEGIS Program Synthesis $	imes$ Zero-Shot Rule Adaptation $	imes$ Multi-Domain Transfer
* **Thực trạng**: Vòng lặp Synthesizer-Verifier (CEGIS) được dùng trong lập trình, nhưng chưa được đưa vào agent chơi game để thích ứng zero-shot.
* **Khoảng trống giao thoa**: Thuật toán **ACE-Tree (Active Counterexample-Guided Tree Synthesis)** cho phép agent tự động sửa trực tiếp đoạn code vá AST ($\Delta_{	ext{patch}}$) ngay trong lượt chơi khi gặp môi trường can thiệp luật, đồng hình (isomorphic) từ 2D Grid sang Minecraft Datapacks và SWE-bench Code ASTs.

---

## III. BẢNG TỔNG HỢP CÁC ĐIỂM GIAO THOA KHOA HỌC

| Điểm Giao Thoa (Intersection) | Các Phân Ngành Tham Gia | Vấn Đề Trước Đây Chưa Giải Quyết | Giải Pháp Giao Thoa Đột Phá | Tác Động Công Bố Target |
| :--- | :--- | :--- | :--- | :--- |
| **Giao Thoa A (Paper 1)** | Subfield 1 $	imes$ Subfield 2 $	imes$ Subfield 3 $	imes$ Subfield 4 | Phải tự tay sửa luật thủ công (Aguilar Martín 2026, MirrorCraft 2026) | Tự động hóa sinh lưu trữ bài test can thiệp luật bằng CMA-ME QD | IEEE Transactions on Games / ACM FDG |
| **Giao Thoa B (Paper 1)** | Subfield 4 $	imes$ Subfield 6 | Bẫy lấy mẫu thụ động $A_{	ext{pred}} \ge 98\% \implies R_{	ext{play}} = 100\%$ | Thuật toán Active Tree Probing chứng minh PAC Bounds $O(k \log(1/\delta))$ | IEEE Transactions on Games / ACM FDG |
| **Giao Thoa C (Paper 2)** | Subfield 1 $	imes$ Subfield 3 $	imes$ Subfield 6 | Agent sụp đổ khi rơi vào thế giới bị can thiệp luật server-side | Thuật toán ACE-Tree tự động vá AST code patch ($\Delta_{	ext{patch}}$) zero-shot | ICLR / NeurIPS / AIJ |
| **Giao Thoa D (Paper 2)** | Subfield 1 $	imes$ Subfield 5 $	imes$ Subfield 6 | Đánh giá bị phụ thuộc vào 1 engine đơn lẻ (PuzzleScript/Sokoban) | Chứng minh đồng hình cấu trúc (Isomorphic Transfer) sang SWE-bench & Minecraft | ICLR / NeurIPS / AIJ |
