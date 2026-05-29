import sys, json
sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json'

with open(REGISTER_PATH, encoding='utf-8') as f:
    data = json.load(f)

data['last_slack_digest'] = {
    "run_number": 18,
    "date": "2026-05-29",
    "channel": "C0B0MB0Q4KD",
    "message_ts": "1780043396.198799",
    "url": "https://superbet.slack.com/archives/C0B0MB0Q4KD/p1780043396198799"
}

with open(REGISTER_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Final state written.")
print(f"last_slack_digest: {data['last_slack_digest']['url']}")
print(f"run_number: {data['run_number']}")
print(f"last_run: {data['last_run']}")
