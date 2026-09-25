import urllib.request
import json
import time
import os

# Landmark papers across 4 key lineages:
# 1. World Models & Planning Adequacy (Dreamer, MuZero, Value Equivalence, Verified World Models)
# 2. Action Model Learning & Inductive Dynamics (PDDLGym, Action Model Learning, Code World Models)
# 3. Procedural Content Generation & QD (MAP-Elites, Quality Diversity, PCG-RL)
# 4. General Game Playing & Rule Interventions (General Game Playing, PuzzleScript, Rule Transfer)

seed_queries = [
    "World Models",
    "Value Equivalence Reinforcement Learning",
    "Action Model Learning PDDL",
    "Code World Models Planning",
    "MAP-Elites Quality Diversity Games",
    "General Game Playing Rule Transfer"
]

print("Searching OpenAlex API for connected paper networks and citations...")
connected_flows = {}

headers = {'User-Agent': 'ThesisResearch/1.0 (mailto:thesis@example.com)'}

for query in seed_queries:
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={encoded_query}&per_page=5&sort=cited_by_count:desc"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            connected_flows[query] = []
            for item in results:
                paper_info = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'publication_year': item.get('publication_year'),
                    'cited_by_count': item.get('cited_by_count'),
                    'doi': item.get('doi'),
                    'primary_location': item.get('primary_location', {}).get('source', {}).get('display_name') if item.get('primary_location') else None,
                    'referenced_works_count': len(item.get('referenced_works', [])),
                    'related_works_count': len(item.get('related_works', []))
                }
                connected_flows[query].append(paper_info)
                print(f"[{query}] -> {item.get('title')} ({item.get('publication_year')}) | Citations: {item.get('cited_by_count')}")
    except Exception as e:
        print(f"Failed query '{query}': {e}")
    time.sleep(1.0)

os.makedirs('literature', exist_ok=True)
with open('literature/openalex_connected_flows.json', 'w', encoding='utf-8') as f:
    json.dump(connected_flows, f, indent=2, ensure_ascii=False)

print("Successfully saved literature/openalex_connected_flows.json")
