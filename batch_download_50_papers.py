import json
import os
import urllib.request
import time
import pymupdf # PyMuPDF

print("=== Starting 50+ Paper PDF Download & Full-Text Conversion Engine ===")

# Read papers from json if exists
papers_to_process = []

if os.path.exists('literature/papers_5yr_2021_2026.json'):
    with open('literature/papers_5yr_2021_2026.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            aid = item.get('arxiv_id') or item.get('id')
            title = item.get('title', 'Untitled Paper')
            if aid and len(aid) > 5 and '.' in aid:
                # Clean aid
                aid_clean = aid.replace('arXiv:', '').strip()
                papers_to_process.append({
                    'id': aid_clean,
                    'title': title,
                    'url': f"https://arxiv.org/pdf/{aid_clean}.pdf"
                })

# Deduplicate
seen = set()
unique_papers = []
for p in papers_to_process:
    if p['id'] not in seen:
        seen.add(p['id'])
        unique_papers.append(p)

print(f"Total unique arXiv papers identified in corpus: {len(unique_papers)}")

# Target top 50 papers
target_batch = unique_papers[:50]

os.makedirs('papers', exist_ok=True)
os.makedirs('papers/images', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

success_count = 0
total_pages_extracted = 0
total_images_extracted = 0

batch_summary = []

for idx, paper in enumerate(target_batch):
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    print(f"\n[{idx+1}/{len(target_batch)}] Processing Paper [{pid}]: {paper['title'][:60]}...")
    
    # Download PDF if missing or empty
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        try:
            req = urllib.request.Request(paper['url'], headers=headers)
            with urllib.request.urlopen(req) as resp, open(pdf_path, 'wb') as f:
                f.write(resp.read())
            print(f"  -> Downloaded PDF ({os.path.getsize(pdf_path)} bytes)")
            time.sleep(1.0)
        except Exception as e:
            print(f"  -> Failed to download PDF for {pid}: {e}")
            continue
            
    # Parse PDF with PyMuPDF
    try:
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        
        extracted_md = []
        extracted_md.append(f"# Full Text & Figure Extraction: {paper['title']}\n\n")
        extracted_md.append(f"- **arXiv ID**: `{pid}`\n")
        extracted_md.append(f"- **Source PDF**: [{pid}.pdf]({pdf_path})\n")
        extracted_md.append(f"- **Total Pages**: {total_pages}\n\n---\n\n")
        
        image_count = 0
        for page_num in range(total_pages):
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
        total_pages_extracted += total_pages
        total_images_extracted += image_count
        
        batch_summary.append({
            'id': pid,
            'title': paper['title'],
            'pages': total_pages,
            'images': image_count,
            'pdf': pdf_path,
            'md': md_path
        })
        print(f"  -> Successfully converted: {total_pages} pages, {image_count} images -> {md_path}")
    except Exception as e:
        print(f"  -> Error converting {pid}: {e}")

print(f"\n=== Batch Execution Finished ===")
print(f"Successfully processed: {success_count} papers")
print(f"Total Pages Extracted: {total_pages_extracted} pages")
print(f"Total Images Extracted: {total_images_extracted} figures")

# Write master index
with open('papers/50_papers_corpus_index.json', 'w', encoding='utf-8') as f:
    json.dump(batch_summary, f, indent=2, ensure_ascii=False)
print("Saved papers/50_papers_corpus_index.json")
