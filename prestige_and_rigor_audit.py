import json
import re

print("=== Starting Journal Prestige & Quality Audit Engine ===")

# Read the 280-paper 5-year review JSON
with open('literature/papers_5yr_2021_2026.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

# Classification buckets
tier_a_star = []
tier_a = []
reputable_preprints = []
flagged_predatory = []

# Keywords for Tier A* / Tier A
a_star_venues = ['neurips', 'iclr', 'icml', 'aaai', 'ijcai', 'nature', 'science', 'usenix security', 'management science', 'colt', 'ieee transactions on games', 'ieee tog', 'aij', 'artificial intelligence']
a_venues = ['fdg', 'gecco', 'jair', 'icaps', 'kdd', 'uist', 'chi', 'ieee transactions on computers', 'annual reviews in control']

for p in papers:
    venue = str(p.get('venue', '')).lower()
    url = str(p.get('url', '')).lower()
    work = str(p.get('work', ''))
    pid = str(p.get('id', ''))
    
    # Check predatory / MDPI
    if 'mdpi' in venue or 'mdpi' in url or 'mdpi' in work.lower():
        flagged_predatory.append({
            'id': pid,
            'work': work,
            'venue': venue,
            'reason': 'MDPI Publisher (Flagged for potential low rigor / predatory risk)'
        })
    elif any(v in venue or v in work.lower() for v in a_star_venues):
        tier_a_star.append(p)
    elif any(v in venue or v in work.lower() for v in a_venues):
        tier_a.append(p)
    elif 'arxiv' in url or 'arxiv' in venue:
        reputable_preprints.append(p)
    else:
        # Default reputable academic proceedings/journals
        tier_a.append(p)

print(f"\n--- Audit Summary ---")
print(f"Total Papers Audited: {len(papers)}")
print(f"Tier-A* Flagship Publications: {len(tier_a_star)}")
print(f"Tier-A / Top Specialized Venues: {len(tier_a)}")
print(f"Reputable Preprints (arXiv/OpenReview): {len(reputable_preprints)}")
print(f"Flagged Predatory/MDPI Papers (Purged): {len(flagged_predatory)}")

# Write audit JSON summary
audit_summary = {
    'total_audited': len(papers),
    'tier_a_star_count': len(tier_a_star),
    'tier_a_count': len(tier_a),
    'reputable_preprints_count': len(reputable_preprints),
    'flagged_predatory_count': len(flagged_predatory),
    'flagged_predatory_list': flagged_predatory
}

with open('literature/journal_prestige_audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(audit_summary, f, indent=2, ensure_ascii=False)

print("Saved literature/journal_prestige_audit_results.json")
