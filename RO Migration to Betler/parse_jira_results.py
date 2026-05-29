import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

infile = r'C:\Users\JonVince\.claude\projects\C--Users-JonVince\1bf7634f-0f8c-447b-8f32-7b954d54eeaa\tool-results\mcp-b846195e-69b9-4ade-88d4-18e6a3f23890-searchJiraIssuesUsingJql-1780038153644.txt'

with open(infile, encoding='utf-8') as f:
    data = json.load(f)

issues = data['issues']['nodes']
print(f"Total issues returned: {len(issues)}")
print()

TODAY = '2026-05-29'

def parse_date(d):
    if not d:
        return None
    return str(d)[:10]

def days_since(date_str):
    from datetime import datetime
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str[:10], '%Y-%m-%d')
        today = datetime.strptime(TODAY, '%Y-%m-%d')
        return (today - d).days
    except:
        return None

for issue in issues:
    key = issue.get('key', '?')
    fields = issue.get('fields', {})
    summary = fields.get('summary', '')[:60]
    status = fields.get('status', {}).get('name', '?') if fields.get('status') else '?'
    issuetype = fields.get('issuetype', {}).get('name', '?') if fields.get('issuetype') else '?'
    prd = parse_date(fields.get('customfield_12114'))
    updated = parse_date(fields.get('updated'))
    stale_days = days_since(updated)
    labels = fields.get('labels', [])

    # Short status update
    ssu_raw = fields.get('customfield_15303', '')
    ssu = ''
    if ssu_raw:
        if isinstance(ssu_raw, dict):
            # ADF format
            ssu = str(ssu_raw)[:200]
        elif isinstance(ssu_raw, str):
            ssu = ssu_raw[:200]

    # Check for risk language
    risk_words = ['blocked', 'at risk', 'delayed', 'dependency', 'blocking']
    negation_pattern = re.compile(r'\b(no|not|without)\b\s+\w+\s+\w+\s+(' + '|'.join(risk_words) + r')', re.IGNORECASE)
    risk_lang_raw = any(w in ssu.lower() for w in risk_words)
    risk_lang_negated = bool(negation_pattern.search(ssu))
    risk_lang = risk_lang_raw and not risk_lang_negated

    # Health status
    health = fields.get('customfield_12114')  # This might not be right - let me check other health field

    flagged = fields.get('flagged', False)

    print(f"KEY={key} | type={issuetype} | status={status} | prd={prd} | updated={updated} | stale={stale_days}d | labels={labels} | risk_lang={risk_lang} | flagged={flagged}")
    print(f"  summary: {summary}")
    if ssu:
        print(f"  ssu: {ssu[:150]}")
    print()
