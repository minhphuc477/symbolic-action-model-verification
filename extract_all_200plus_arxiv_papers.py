import json
import os
import urllib.request
import time
import re
import pymupdf # PyMuPDF

print("=== Starting Full 200+ Paper 5-Year Literature PDF Download & Conversion Engine ===")

# Read the full 280-paper dataset
with open('literature/papers_5yr_2021_2026.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_papers = []

for item in data:
    url = item.get('url', '')
    title = item.get('work', 'Untitled Paper')
    pid = item.get('id', '')
    venue = item.get('venue', 'Academic Venue')
    year = item.get('year', 2026)
    area = item.get('area', 'Game AI')
    method = item.get('method', '')
    evidence = item.get('evidence', '')
    limitation = item.get('limitation', '')
    
    # Extract arXiv ID if present
    m = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', url)
    if m:
        aid = m.group(1)
        all_papers.append({
            'id': aid,
            'ledger_id': pid,
            'title': title,
            'year': year,
            'venue': venue,
            'area': area,
            'url': f"https://arxiv.org/pdf/{aid}.pdf",
            'method': method,
            'evidence': evidence,
            'limitation': limitation
        })

# Deduplicate
seen = set()
unique_papers = []
for p in all_papers:
    if p['id'] not in seen:
        seen.add(p['id'])
        unique_papers.append(p)

print(f"Total Unique arXiv Papers Identified for Download (2021-2026): {len(unique_papers)}")

os.makedirs('papers', exist_ok=True)
os.makedirs('papers/images', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

success_count = 0
total_pages = 0
total_images = 0

corpus_summary = []

for idx, paper in enumerate(unique_papers):
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    print(f"\n[{idx+1}/{len(unique_papers)}] Processing Paper [{pid}] ({paper['venue']}): {paper['title'][:65]}...")
    
    # Download PDF if not present
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        try:
            req = urllib.request.Request(paper['url'], headers=headers)
            with urllib.request.urlopen(req) as resp, open(pdf_path, 'wb') as f:
                f.write(resp.read())
            print(f"  -> Downloaded PDF ({os.path.getsize(pdf_path)} bytes)")
            time.sleep(1.0)
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
        extracted_md.append(f"- **Ledger ID**: `{paper['ledger_id']}`\n")
        extracted_md.append(f"- **Venue & Year**: `{paper['venue']}` ({paper['year']})\n")
        extracted_md.append(f"- **Area**: {paper['area']}\n")
        extracted_md.append(f"- **Source PDF**: [{pid}.pdf]({pdf_path})\n")
        extracted_md.append(f"- **Total Pages**: {pages_count}\n\n---\n\n")
        extracted_md.append(f"## Executive Summary & Findings\n")
        extracted_md.append(f"- **Key Method**: {paper['method']}\n")
        extracted_md.append(f"- **Empirical Evidence**: {paper['evidence']}\n")
        extracted_md.append(f"- **Limitations & Boundaries**: {paper['limitation']}\n\n---\n\n")
        
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
            'ledger_id': paper['ledger_id'],
            'title': paper['title'],
            'year': paper['year'],
            'venue': paper['venue'],
            'area': paper['area'],
            'pages': pages_count,
            'images': image_count,
            'pdf': pdf_path,
            'md': md_path
        })
        print(f"  -> Converted: {pages_count} pages, {image_count} figures -> {md_path}")
    except Exception as e:
        print(f"  -> Failed parsing PDF for {pid}: {e}")

print(f"\n=== Full 200+ Paper Batch Execution Completed ===")
print(f"Total Papers Processed: {success_count} papers")
print(f"Total Pages Extracted: {total_pages} pages")
print(f"Total Figures Extracted: {total_images} figures")

with open('papers/all_200plus_papers_corpus_index.json', 'w', encoding='utf-8') as f:
    json.dump(corpus_summary, f, indent=2, ensure_ascii=False)
print("Saved papers/all_200plus_papers_corpus_index.json")
