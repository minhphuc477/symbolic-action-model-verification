import openpyxl
import pandas as pd
import json

excel_file = 'ai_games_research_ledger_2026-09-09_v50_external_runtime_harness.xlsx'
wb = openpyxl.load_workbook(excel_file, data_only=True)

print(f"=== Auditing Excel Ledger: {excel_file} ===")
print(f"Total Sheets: {len(wb.sheetnames)}")

sheets_to_audit = [
    'Dashboard',
    'v50 External Runtime Harness',
    'v49 External Replication Audit',
    'v46 E0 Execution Results',
    'v45 E0 Protocol Lock',
    'v44 G078-R Burden Audit',
    'Limitations & Kill Tests',
    'T002 Gap Audit',
    'Game Field Landscape',
    'v38 GameAI Field Reset'
]

audit_results = {}

for sheet in sheets_to_audit:
    if sheet in wb.sheetnames:
        ws = wb[sheet]
        data = list(ws.values)
        if data:
            headers = data[0]
            rows = data[1:15] # top 15 rows
            audit_results[sheet] = {
                'headers': [str(h) for h in headers if h is not None],
                'sample_rows': [[str(cell) if cell is not None else '' for cell in r] for r in rows[:5]]
            }
            print(f"\n--- Sheet: [{sheet}] ---")
            print(f"Headers: {headers[:8]}")
            for r in rows[:3]:
                print(f"  Row: {r[:6]}")

with open('literature/excel_v50_audit_summary.json', 'w', encoding='utf-8') as f:
    json.dump(audit_results, f, indent=2, ensure_ascii=False)

print("\nSaved literature/excel_v50_audit_summary.json")
