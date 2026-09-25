import os
import urllib.request
import time
import pymupdf # PyMuPDF

target_papers = [
    {
        'id': '2002.04513',
        'title': 'Objective Mismatch in Model-Based Reinforcement Learning',
        'url': 'https://arxiv.org/pdf/2002.04513.pdf'
    },
    {
        'id': '1907.07003',
        'title': 'Learning Action Models with SAT (FAMA)',
        'url': 'https://arxiv.org/pdf/1907.07003.pdf'
    },
    {
        'id': '2005.02327',
        'title': 'Learning Action Models with Answer Set Programming (FastLAS)',
        'url': 'https://arxiv.org/pdf/2005.02327.pdf'
    },
    {
        'id': '2109.06780',
        'title': 'Benchmarking the Spectrum of Agent Capabilities (Crafter)',
        'url': 'https://arxiv.org/pdf/2109.06780.pdf'
    },
    {
        'id': '2102.12375',
        'title': 'Transfer of Fully Convolutional Policy-Value Networks Between Games and Game Variants (Ludii)',
        'url': 'https://arxiv.org/pdf/2102.12375.pdf'
    },
    {
        'id': '2607.14169',
        'title': 'When a Verified World Model Still Loses: Play-Adequacy vs Prediction-Accuracy in LLM-Synthesized Code World Models',
        'url': 'https://arxiv.org/pdf/2607.14169.pdf'
    },
    {
        'id': '2607.29218',
        'title': 'MirrorCraft: Paired Evaluation under Hidden Rule Changes in Minecraft',
        'url': 'https://arxiv.org/pdf/2607.29218.pdf'
    }
]

os.makedirs('papers', exist_ok=True)
os.makedirs('papers/images', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== Downloading & Converting Core Action Model Papers ===")

for paper in target_papers:
    pid = paper['id']
    pdf_path = f"papers/{pid}.pdf"
    md_path = f"papers/{pid}_fulltext.md"
    
    try:
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
            print(f"Downloading [{pid}]: {paper['title']}...")
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
        print(f"Successfully converted [{pid}]: {total_pages} pages, {image_count} images -> {md_path}")
    except Exception as err:
        print(f"Failed processing [{pid}]: {err}")

print("=== Core Action Model Papers Ready ===")
