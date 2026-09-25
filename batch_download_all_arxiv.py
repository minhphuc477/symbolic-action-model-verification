import json
import os
import urllib.request
import time
import re
import pymupdf # PyMuPDF

print("=== Starting 50+ Paper arXiv PDF Downloader & Full-Text Converter ===")

with open('literature/papers_5yr_2021_2026.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

extracted_arxiv = []

for item in data:
    url = item.get('url', '')
    title = item.get('work', 'Untitled Paper')
    pid = item.get('id', '')
    
    # Check arXiv pattern in url
    m = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', url)
    if m:
        aid = m.group(1)
        extracted_arxiv.append({
            'id': aid,
            'title': title,
            'url': f"https://arxiv.org/pdf/{aid}.pdf",
            'ledger_id': pid
        })

# Explicit landmark papers across 7 Game AI subfields
landmark_papers = [
    {'id': '2607.14169', 'title': 'When a Verified World Model Still Loses: Play-Adequacy vs Prediction-Accuracy', 'url': 'https://arxiv.org/pdf/2607.14169.pdf', 'ledger_id': 'L446'},
    {'id': '2607.29218', 'title': 'MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft', 'url': 'https://arxiv.org/pdf/2607.29218.pdf', 'ledger_id': 'L447'},
    {'id': '2402.12275', 'title': 'WorldCoder: Building World Models via Code Generation for Model-Based LLM Agents', 'url': 'https://arxiv.org/pdf/2402.12275.pdf', 'ledger_id': 'L205'},
    {'id': '2604.24062', 'title': 'Grounding Before Generalizing: How AI Differs from Humans in Causal Transfer', 'url': 'https://arxiv.org/pdf/2604.24062.pdf', 'ledger_id': 'L450'},
    {'id': '2609.09163', 'title': 'World-Time Compute with Verified Code World Models', 'url': 'https://arxiv.org/pdf/2609.09163.pdf', 'ledger_id': 'L451'},
    {'id': '2603.15798', 'title': 'CUBE: A Standard for Unifying Agent Benchmarks', 'url': 'https://arxiv.org/pdf/2603.15798.pdf', 'ledger_id': 'L452'},
    {'id': '2508.14704', 'title': 'MCP-Universe: Benchmarking Large Language Models with Real-World Model Context Protocol Servers', 'url': 'https://arxiv.org/pdf/2508.14704.pdf', 'ledger_id': 'L453'},
    {'id': '2606.15032', 'title': 'How Should World Models Be Evaluated for Embodied Decision-Making?', 'url': 'https://arxiv.org/pdf/2606.15032.pdf', 'ledger_id': 'L454'},
    {'id': '2609.14995', 'title': 'Intelligence Under Time Constraints: Rethinking Test-Time Compute in Agentic World Models', 'url': 'https://arxiv.org/pdf/2609.14995.pdf', 'ledger_id': 'L455'},
    {'id': '2501.12948', 'title': 'DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning', 'url': 'https://arxiv.org/pdf/2501.12948.pdf', 'ledger_id': 'L456'},
    {'id': '2609.26293', 'title': 'Dual-Frontier: When Can an Agent Trust Its World Model under Rule Interventions?', 'url': 'https://arxiv.org/pdf/2609.26293.pdf', 'ledger_id': 'L457'},
    {'id': '2505.18102', 'title': 'Zero-Shot Rule Adaptation in Gridworld Games: A Human-LLM Comparative Study', 'url': 'https://arxiv.org/pdf/2505.18102.pdf', 'ledger_id': 'L458'},
    {'id': '2608.29998', 'title': 'The Intervention Gap in Latent World Models', 'url': 'https://arxiv.org/pdf/2608.29998.pdf', 'ledger_id': 'L459'},
    {'id': '2602.11389', 'title': 'Learning World Models through Object-Level Latent Masking (Causal-JEPA)', 'url': 'https://arxiv.org/pdf/2602.11389.pdf', 'ledger_id': 'L460'},
    {'id': '2504.11209', 'title': 'PAC-MDP World Model Bounds under Sparse Interventions', 'url': 'https://arxiv.org/pdf/2504.11209.pdf', 'ledger_id': 'L461'}
]

all_target_papers = landmark_papers + extracted_arxiv

# Deduplicate by paper id
seen = set()
unique_target_papers = []
for p in all_target_papers:
    if p['id'] not in seen:
        seen.add(p['id'])
        unique_target_papers.append(p)

print(f"Total Unique arXiv Papers Identified for Download: {len(unique_target_papers)}")

# Limit to top 50 papers for batch run
target_batch = unique_target_papers[:50]

os.makedirs('papers', exist_ok=True)
os.makedirs('papers/images', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

success_count = 0
total_pages = 0
total_images = 0

corpus_summary = []

for idx, paper in enumerate(target_batch):
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    print(f"\n[{idx+1}/{len(target_batch)}] Processing Paper [{pid}]: {paper['title'][:60]}...")
    
    # Download PDF if not present
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        try:
            req = urllib.request.Request(paper['url'], headers=headers)
            with urllib.request.urlopen(req) as resp, open(pdf_path, 'wb') as f:
                f.write(resp.read())
            print(f"  -> Downloaded PDF ({os.path.getsize(pdf_path)} bytes)")
            time.sleep(1.2)
        except Exception as e:
            print(f"  -> Download failed for {pid}: {e}")
            continue
    else:
        print(f"  -> Existing PDF found ({os.path.getsize(pdf_path)} bytes)")
        
    # Convert PDF using PyMuPDF
    try:
        doc = pymupdf.open(pdf_path)
        pages_count = len(doc)
        
        extracted_md = []
        extracted_md.append(f"# Full Text & Figure Extraction: {paper['title']}\n\n")
        extracted_md.append(f"- **arXiv ID**: `{pid}`\n")
        extracted_md.append(f"- **Ledger ID**: `{paper.get('ledger_id', 'N/A')}`\n")
        extracted_md.append(f"- **Source PDF**: [{pid}.pdf]({pdf_path})\n")
        extracted_md.append(f"- **Total Pages**: {pages_count}\n\n---\n\n")
        
        image_count = 0
        for page_num in range(pages_count):
            page = doc[page_num]
            text = page.get_text("text")
            
            extracted_md.append(f"## Page {page_num + 1}\n\n")
            extracted_md.append(text + "\n\n")
            
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    img_filename = f"{pid}_img_P{page_num + 1}_{img_index + 1}.{image_ext}"
                    img_save_path = f"papers/images/{img_filename}"
                    
                    with open(img_save_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    image_count += 1
                    extracted_md.append(f"![Figure P{page_num + 1}-{img_index + 1}](images/{img_filename})\n*Figure P{page_num + 1}-{img_index + 1} (Page {page_num + 1})*\n\n")
                except Exception as e:
                    pass
                    
        doc.close()
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("".join(extracted_md))
            
        success_count += 1
        total_pages += pages_count
        total_images += image_count
        
        corpus_summary.append({
            'id': pid,
            'title': paper['title'],
            'pages': pages_count,
            'images': image_count,
            'pdf': pdf_path,
            'md': md_path
        })
        print(f"  -> Successfully converted: {pages_count} pages, {image_count} images -> {md_path}")
    except Exception as e:
        print(f"  -> Failed parsing PDF for {pid}: {e}")

print(f"\n=== Batch Execution Completed ===")
print(f"Total Papers Processed: {success_count} papers")
print(f"Total Pages Extracted: {total_pages} pages")
print(f"Total Figures Extracted: {total_images} figures")

with open('papers/50_papers_corpus_index.json', 'w', encoding='utf-8') as f:
    json.dump(corpus_summary, f, indent=2, ensure_ascii=False)
print("Saved papers/50_papers_corpus_index.json")
