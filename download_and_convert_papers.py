import os
import urllib.request
import time
import pymupdf # PyMuPDF

target_papers = [
    {
        'id': '2607.14169',
        'title': 'When a Verified World Model Still Loses: Play-Adequacy vs Prediction-Accuracy in LLM-Synthesized Code World Models',
        'url': 'https://arxiv.org/pdf/2607.14169.pdf'
    },
    {
        'id': '2607.29218',
        'title': 'MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft',
        'url': 'https://arxiv.org/pdf/2607.29218.pdf'
    },
    {
        'id': '2402.12275',
        'title': 'WorldCoder: Building World Models via Code Generation for Model-Based LLM Agents',
        'url': 'https://arxiv.org/pdf/2402.12275.pdf'
    },
    {
        'id': '2604.24062',
        'title': 'Grounding Before Generalizing: How AI Differs from Humans in Causal Transfer',
        'url': 'https://arxiv.org/pdf/2604.24062.pdf'
    },
    {
        'id': '2609.09163',
        'title': 'World-Time Compute with Verified Code World Models',
        'url': 'https://arxiv.org/pdf/2609.09163.pdf'
    },
    {
        'id': '2603.15798',
        'title': 'CUBE: A Standard for Unifying Agent Benchmarks',
        'url': 'https://arxiv.org/pdf/2603.15798.pdf'
    }
]

os.makedirs('papers', exist_ok=True)
os.makedirs('papers/images', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== Running Robust PyMuPDF PDF Text & Image Converter ===")

for paper in target_papers:
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
        print(f"Downloading {pid}...")
        req = urllib.request.Request(paper['url'], headers=headers)
        with urllib.request.urlopen(req) as resp, open(pdf_path, 'wb') as f:
            f.write(resp.read())
        time.sleep(1.0)
        
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
    print(f"Successfully converted [{pid}]: {total_pages} pages, {image_count} images extracted -> {md_path}")

print("=== All PDF Conversions Successfully Finalized ===")
