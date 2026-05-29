import sys, json
sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json'

with open(REGISTER_PATH, encoding='utf-8') as f:
    data = json.load(f)

risks = data['risks']
risk_map = {r['id']: r for r in risks}

# Record RR-052 Notion page ID
risk_map['RR-052']['notion_page_id'] = '36f032f852c5818b9675daa3ce97c4f5'

# Update last_slack_digest will be done after posting — placeholder not needed now
# Confirm notion_sync_skipped_this_run = False (sync succeeded)
data['notion_sync_skipped_this_run'] = False

with open(REGISTER_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Final register written.")
print(f"RR-052 notion_page_id: {risk_map['RR-052']['notion_page_id']}")

# Print digest data summary
escalated = [r for r in risks if r.get('status') == 'Escalated']
print(f"\nEscalated ({len(escalated)}):")
for r in escalated:
    print(f"  {r['id']} | score={r['score']} | {r['title'][:60]}")

changed_up = [r for r in risks if r.get('trend') == 'up' and r.get('status') not in ['Closed', 'Resolved'] and r.get('score', 0) > 0]
changed_down = [r for r in risks if r.get('trend') == 'down' and r.get('status') not in ['Closed', 'Resolved']
                and r.get('score_last_run', 0) >= 6 and r.get('score', 0) < 6]

print(f"\nScore up (active, score>0):")
for r in changed_up:
    print(f"  {r['id']} | {r.get('score_last_run',0)}→{r['score']} | {r['title'][:50]}")

print(f"\nDe-escalated (was >=6, now <6):")
for r in changed_down:
    print(f"  {r['id']} | {r.get('score_last_run',0)}→{r['score']} | {r['title'][:50]}")
