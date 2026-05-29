import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

infile = r'C:\Users\JonVince\.claude\projects\C--Users-JonVince\1bf7634f-0f8c-447b-8f32-7b954d54eeaa\tool-results\mcp-b846195e-69b9-4ade-88d4-18e6a3f23890-searchJiraIssuesUsingJql-1780038153644.txt'

with open(infile, encoding='utf-8') as f:
    data = json.load(f)

issues = data['issues']['nodes']

# Print all custom fields for the first issue to understand structure
if issues:
    print("=== FIELD KEYS for first issue ===")
    fields = issues[0].get('fields', {})
    for k, v in fields.items():
        if v is not None and v != '' and v != [] and v != {}:
            val_str = str(v)[:100]
            print(f"  {k}: {val_str}")
    print()

# Now print health + ssu for all
print("=== HEALTH + SSU ANALYSIS ===")
for issue in issues:
    key = issue.get('key', '?')
    fields = issue.get('fields', {})

    # Look for any field with health/color/status keywords
    health_fields = {}
    for k, v in fields.items():
        if v and isinstance(v, dict):
            name = v.get('name', '')
            color = v.get('color', '')
            if color or 'red' in str(v).lower() or 'amber' in str(v).lower() or 'green' in str(v).lower():
                health_fields[k] = v

    ssu = fields.get('customfield_15303', '')
    ssu_str = ''
    if ssu:
        if isinstance(ssu, str):
            ssu_str = ssu[:200]
        elif isinstance(ssu, dict):
            # Try to extract text from ADF
            ssu_str = str(ssu)[:200]
        elif isinstance(ssu, list):
            ssu_str = str(ssu)[:200]

    print(f"KEY={key}")
    if health_fields:
        print(f"  health_fields: {health_fields}")
    if ssu_str:
        print(f"  ssu: {ssu_str}")
    else:
        print(f"  ssu: (empty)")
    print()
