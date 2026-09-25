import json

with open('literature/detailed_paper_breakdown.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

md_lines = []
md_lines.append("# BÁO CÁO ĐỌC SÂU: PHƯƠNG PHÁP (METHODS), KẾT QUẢ (RESULTS) VÀ GIỚI HẠN (LIMITATIONS) CÁC BÀI BÁO 2021–2026\n")
md_lines.append("> **Nguồn dữ liệu**: Sổ ký lục nghiên cứu `ai_games_research_ledger_2026-09-09_v50_external_runtime_harness.xlsx`\n")
md_lines.append(f"> **Tổng số công trình phân tích chi tiết**: {len(papers)} bài báo (2021–2026)\n\n---\n")

# Highlight key landmark papers with full details
key_ids = [
    "L446", "L447", "L445", "L444", "L453", "L448", "L452", "L451", 
    "L430", "L431", "L432", "L424", "L425", "L415", "L422", "L420", 
    "L437", "L440", "L441", "L442", "L443", "L454", "L455", "L456", "L457", "L458"
]

md_lines.append("## I. PHÂN TÍCH CHI TIẾT CÁC CÔNG TRÌNH ĐỘT PHÁ CỐT LÕI (LANDMARK PAPERS)\n")

for p in papers:
    pid = p['id']
    if pid in key_ids or any(k in pid for k in ["L44", "L45", "L43"]):
        md_lines.append(f"### [{pid}] {p['work']} ({p['year']})")
        md_lines.append(f"- **Tạp chí / Hội nghị**: `{p['venue']}`")
        md_lines.append(f"- **Lĩnh vực / Area**: `{p['area']}`")
        md_lines.append(f"- **Phương pháp (Key Method / Setting)**:\n  {p['method']}")
        md_lines.append(f"- **Kết quả thực nghiệm (Key Evidence / Results)**:\n  {p['results']}")
        md_lines.append(f"- **Giới hạn & Điều kiện biên (Limitations & Boundaries)**:\n  {p['limitations']}\n")
        md_lines.append("---\n")

md_lines.append("## II. BẢNG TỔNG HỢP PHƯƠNG PHÁP, KẾT QUẢ & GIỚI HẠN TOÀN BỘ 280 BÀI BÁO (2021–2026)\n")
md_lines.append("| ID | Bài báo (Work & Year) | Tạp chí | Phương pháp (Methods) | Kết quả (Results / Evidence) | Giới hạn (Limitations) |")
md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

for p in papers:
    w = p['work'].replace('|', '/')
    v = p['venue'].replace('|', '/')
    m = p['method'].replace('|', '/').replace('\n', ' ')
    r = p['results'].replace('|', '/').replace('\n', ' ')
    l = p['limitations'].replace('|', '/').replace('\n', ' ')
    md_lines.append(f"| **{p['id']}** | {w} ({p['year']}) | {v} | {m} | {r} | {l} |")

with open('literature/detailed_methods_results_limitations.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print("Successfully generated literature/detailed_methods_results_limitations.md")
