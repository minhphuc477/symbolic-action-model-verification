import urllib.request
import json
import time
import os

arxiv_ids = [
    '2607.14169', # Aguilar Martin 2026
    '2607.29218', # MirrorCraft 2026
    '2002.06432', # PDDLGym 2020
    '1909.07750', # MDP Playground
    '2106.10316', # Proper Value Equivalence
    '2003.00030', # Policy-Aware Model Learning
]

print("Querying Semantic Scholar API for paper citation graphs...")
flows_data = {}

for aid in arxiv_ids:
    url = f"https://api.semanticscholar.org/graph/v1/paper/ARXIV:{aid}?fields=title,year,citationCount,referenceCount,citations.title,citations.year,references.title,references.year"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get('title', 'Unknown')
            cite_cnt = data.get('citationCount', 0)
            ref_cnt = data.get('referenceCount', 0)
            
            top_refs = sorted([r for r in data.get('references', []) if r and r.get('year')], key=lambda x: x.get('year', 0), reverse=True)[:5]
            top_cites = sorted([c for c in data.get('citations', []) if c and c.get('year')], key=lambda x: x.get('year', 0), reverse=True)[:5]
            
            flows_data[aid] = {
                'title': title,
                'year': data.get('year'),
                'citationCount': cite_cnt,
                'referenceCount': ref_cnt,
                'top_references': top_refs,
                'top_citations': top_cites
            }
            print(f"Fetched [{aid}]: {title} | Citations: {cite_cnt} | Refs: {ref_cnt}")
    except Exception as e:
        print(f"Failed {aid}: {e}")
    time.sleep(1.5)

os.makedirs('literature', exist_ok=True)
with open('literature/semantic_scholar_flows.json', 'w', encoding='utf-8') as f:
    json.dump(flows_data, f, indent=2, ensure_ascii=False)
print("Saved literature/semantic_scholar_flows.json")
