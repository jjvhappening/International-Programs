import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json', encoding='utf-8') as f:
    data = json.load(f)

risks = data.get('risks', [])

# Print the full structure of a few escalated risks
escalated = [r for r in risks if r.get('status') == 'Escalated']
print(f"=== ESCALATED RISK SAMPLE (first 2) ===")
for r in escalated[:2]:
    print(json.dumps(r, indent=2, ensure_ascii=False))
    print()

# Also check what signal keys exist
print("=== ALL SIGNAL KEYS ===")
all_keys = set()
for r in risks:
    if r.get('signals'):
        all_keys.update(r['signals'].keys() if isinstance(r['signals'], dict) else [])
print(sorted(all_keys))
