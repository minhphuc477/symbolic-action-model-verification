import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import time
import os

arxiv_queries = [
    ("2607.14169", "When a Verified World Model Still Loses"),
    ("2607.29218", "MirrorCraft Paired Evaluation"),
    ("2410.17859", "GIF-MCTS LLM Code World Models"),
    ("2602.11389", "Causal-JEPA Learning World Models"),
    ("2604.24062", "Grounding Before Generalizing Causal Transfer"),
    ("2002.06432", "PDDLGym Gym Environments"),
]

flows = {}

for aid, title_hint in arxiv_queries:
    url = f"https://export.arxiv.org/api/query?id_list={aid}"
    print(f"Fetching arXiv record for [{aid}]...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            root = ET.fromstring(data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            if entry is not None:
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                published = entry.find('atom:published', ns).text.strip()
                authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                doi = entry.find('atom:doi', ns)
                doi_str = doi.text if doi is not None else None
                
                flows[aid] = {
                    'arxiv_id': aid,
                    'title': title,
                    'authors': authors,
                    'published': published,
                    'summary': summary,
                    'doi': doi_str
                }
                print(f"Successfully retrieved [{aid}]: {title[:60]}...")
    except Exception as e:
        print(f"Failed {aid}: {e}")
    time.sleep(3) # arXiv rate limit rule (1 request per 3s)

os.makedirs('literature', exist_ok=True)
with open('literature/arxiv_verified_flows.json', 'w', encoding='utf-8') as f:
    json.dump(flows, f, indent=2, ensure_ascii=False)
print("Saved literature/arxiv_verified_flows.json")
