import sys, json
sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json'

with open(REGISTER_PATH, encoding='utf-8') as f:
    data = json.load(f)

risks = data['risks']
risk_map = {r['id']: r for r in risks}

# Record PLAYER-11 comment posted this run
r14 = risk_map['RR-014']
r14['comments_posted'].append({
    "jira_key": "PLAYER-11",
    "date": "2026-05-29",
    "run_number": 18,
    "comment_id": "1281647"
})

# Update epic_context note for RR-002 to reflect label was not physically present in Jira
r02 = risk_map['RR-002']
if r02.get('epic_context'):
    r02['epic_context']['note'] = (r02['epic_context'].get('note', '') +
        ' Label ro-not-closed-out confirmed absent from Jira (never physically stamped). No Jira edit needed.')

# Set notion_sync_skipped_this_run = False (will update if needed)
data['notion_sync_skipped_this_run'] = False

with open(REGISTER_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("CHECKPOINT written.")
print("RR-014 comments_posted:")
for c in risk_map['RR-014']['comments_posted']:
    print(f"  run {c['run_number']}: {c['jira_key']} | {c['date']} | id={c.get('comment_id','?')}")
