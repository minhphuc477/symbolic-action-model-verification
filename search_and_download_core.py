import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
import pymupdf

queries = [
    ("Objective Mismatch Model-Based Reinforcement Learning", "Objective Mismatch"),
    ("Action Model Learning with Guarantees", "Aineto AAAI24 Action Models"),
    ("FastLAS Answer Set Programming", "FastLAS ILP"),
    ("Learning Action Models", "General Action Model Learning"),
    ("Spurious Paths Planning Abstraction", "Spurious Paths Abstraction")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

os.makedirs("papers", exist_ok=True)
os.makedirs("papers/images", exist_ok=True)

print("=== Searching arXiv & Downloading Exact Full-Text PDFs ===")

found_papers = []

for q, label in queries:
    search_url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(q)}&start=0&max_results=3"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            for entry in entries:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
                id_url = entry.find('{http://www.w3.org/2005/Atom}id').text
                arxiv_id = id_url.split('/')[-1].split('v')[0]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                found_papers.append({
                    'id': arxiv_id,
                    'title': title,
                    'label': label,
                    'pdf_url': pdf_url
                })
                print(f"FOUND [{arxiv_id}]: {title} ({label})")
    except Exception as e:
        print(f"Error searching '{q}': {e}")
    time.sleep(1.0)

# Deduplicate
unique_papers = {p['id']: p for p in found_papers}.values()

print(f"\n=== Converting {len(unique_papers)} Papers to Full-Text Markdown ===")

for paper in unique_papers:
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    try:
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
            print(f"Downloading [{pid}]: {paper['title']}...")
            req = urllib.request.Request(paper['pdf_url'], headers=headers)
            with urllib.request.urlopen(req) as resp, open(pdf_path, 'wb') as f:
                f.write(resp.read())
            time.sleep(1.0)
            
        doc = pymupdf.open(pdf_path)
        total_pages = len(doc)
        extracted_md = []
        extracted_md.append(f"# Full Text & Figure Extraction: {paper['title']}\n\n")
        extracted_md.append(f"- **arXiv ID**: `{pid}`\n")
        extracted_md.append(f"- **Label**: `{paper['label']}`\n")
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
        print(f"Successfully processed [{pid}]: {total_pages} pages, {image_count} images -> {md_path}")
    except Exception as err:
        print(f"Failed processing [{pid}]: {err}")

print("=== Search & Extraction Complete ===")
