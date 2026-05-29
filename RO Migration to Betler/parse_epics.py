import sys, json
sys.stdout.reconfigure(encoding='utf-8')

infile = r'C:\Users\JonVince\.claude\projects\C--Users-JonVince\1bf7634f-0f8c-447b-8f32-7b954d54eeaa\tool-results\mcp-b846195e-69b9-4ade-88d4-18e6a3f23890-searchJiraIssuesUsingJql-1780041806847.txt'

with open(infile, encoding='utf-8') as f:
    data = json.load(f)

issues = data['issues']['nodes']
print(f"GAM-10668 child epics: {len(issues)}")
for issue in issues:
    key = issue.get('key', '?')
    fields = issue.get('fields', {})
    summary = fields.get('summary', '')[:60]
    status = fields.get('status', {}).get('name', '?') if fields.get('status') else '?'
    print(f"  {key}: {status} - {summary}")
