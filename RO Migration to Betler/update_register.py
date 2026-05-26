import json, sys
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json'
TODAY = '2026-05-26'
RUN_NUMBER = 15

# Run 15 computed scores for all active risks.
# Format: id_num → (new_score, signals, new_consecutive_misses, status_override)
# - status_override None = auto-determine from score/suppressed state
# - Closed risks (ids 1,3,5,6,7,8,9,10,18,26) are not in this dict and are preserved as-is
UPDATES = {
    2:  (5,  ['Slack-risk-language(2)', 'Slack-5+replies(3)'],
         0, 'open'),        # PLAYER-1299: dropping from Escalated (was 7)
    4:  (5,  ['Stale-19d-in-delivery(2)', 'Slack-risk-language(2)', 'Slack-mention(1)'],
         0, 'open'),        # DAP-3: suppressed, dropping from Escalated (was 6)
    11: (0,  [], 0, 'open'),     # PLAYER-102: suppressed, no signals (was 7)
    12: (0,  [], 0, None),       # PLAYER-220: in_progress_overdue DQ, no signals (was 0)
    13: (0,  [], 0, None),       # PLAYER-1177: updated today, stale gone (was 4)
    14: (3,  ['Slack-risk-language(2)', 'Slack-mention(1)'],
         0, 'open'),        # PLAYER-11: dropping from Escalated (was 6)
    15: (0,  [], 0, None),       # PLAYER-80: no signals (was 2)
    16: (0,  [], 0, None),       # SPORTS-562: no signals (was 1)
    17: (6,  ['Stale-Xd-in-delivery(2)', 'Slack-mention(1)',
              'Timeline-amplifier-x2.0-PRD-May-29'],
         0, 'Escalated'),   # GAM-8800: NEW escalation (was 4, PRD May 29)
    19: (0,  [], 0, 'open'),     # PLT-330: wallet header resolved (was 16!)
    20: (0,  [], 0, None),       # DAP-36: no signals (was 2)
    21: (0,  [], 0, None),       # PLAYER-218: in_progress_overdue DQ (was 0)
    22: (0,  [], 0, None),       # PLAYER-82: no signals (was 2)
    23: (2,  ['Stale-Xd-pre-delivery(1)',
              'Timeline-amplifier-x2.0-PRD-Jun-01'],
         0, 'open'),        # PLAYER-172: dropping from Escalated (was 8)
    24: (0,  [], 0, None),       # PLAYER-1067: no signals (was 0)
    25: (0,  [], 0, None),       # PLAYER-1293: no signals (was 0)
    27: (0,  [], 0, None),       # PLAYER-992: no signals (was 2)
    28: (2,  ['Stale-25d-in-delivery(2)'],
         0, None),          # SOC-3527: staleness only (was 3)
    29: (6,  ['Stale-Xd-in-delivery(2)', 'Slack-mention(1)',
              'Timeline-amplifier-x2.0-PRD-May-29'],
         0, None),          # GAM-10668: suppressed, score UP (was 4); stays suppressed
    30: (0,  [], 0, None),       # PLAYER-1041: no signals (was 3)
    31: (1,  ['Stale-62d-pre-delivery(1)'],
         0, None),          # DAP-42: staleness only (was 1, unchanged)
    32: (0,  [], 0, None),       # GAM-10669: no signals (was 2)
    33: (1,  ['Slack-mention(1)'],
         0, None),          # PLAYER-869: minor Slack signal (was 3)
    34: (0,  [], 0, None),       # PLAYER-921: no signals (was 2)
    35: (0,  [], 0, None),       # PLAYER-1063: no signals (was 2)
    36: (0,  [], 0, None),       # PLAYER-1064: no signals (was 2)
    37: (0,  [], 0, None),       # PLAYER-169: no signals (was 2)
    38: (0,  [], 0, None),       # GAM-8604: no signals (was 2)
    39: (4,  ['Jira-risk(2)', 'Timeline-amplifier-x2.0-PRD-Jun-01'],
         0, 'open'),        # GAM-11474: dropping from Escalated (was 11)
    40: (4,  ['Slack-risk-language(2)',
              'Timeline-amplifier-x2.0-PRD-May-29'],
         0, None),          # GAM-10782: UP from 2, PRD May 29 amplifier
    41: (14, ['Blocked-Status(3)', 'Slack-risk-language(2)',
              'Cross-source-bonus(2)',
              'Timeline-amplifier-x2.0-PRD-May-29'],
         0, 'Escalated'),   # GAM-11319: still top risk (was 15)
    42: (0,  [], 0, None),       # GAM-10333: updated, stale gone (was 6)
    43: (2,  ['Slack-risk-language(2)'],
         0, None),          # Betslip Ticket Search: found via Slack, misses reset (was 0, misses=1)
    44: (0,  [], 2, 'Closed'),   # PLAYER-105: misses=1→2→Closed
    45: (0,  [], 0, None),       # PLAYER-1425: no signals (was 5)
    46: (2,  ['Slack-risk-language(2)'],
         0, None),          # Pateplay: Slack signal (was 4)
    47: (1,  ['Stale-Xd-pre-delivery(1)'],
         0, None),          # SPORTS-1097: staleness only (was 3)
    48: (0,  [], 0, None),       # PLAYER-1070: no signals (was 5)
    49: (3,  ['Slack-risk-language(2)', 'Slack-mention(1)'],
         0, None),          # PLAYER-888/Nuvei: Slack signals (was 4)
    50: (0,  [], 1, 'Resolved'), # Virtual Sports: not detected → misses=1→Resolved
}

def severity_from_score(s):
    if s >= 6: return 'high'
    if s >= 3: return 'medium'
    return 'low'

def id_to_num(rid):
    try:
        return int(str(rid).replace('RR-', ''))
    except:
        return -1

with open(REGISTER_PATH, encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded register: run {data.get('run_number')}, {len(data['risks'])} risks, last_run={data.get('last_run')}")

changes = []
for risk in data['risks']:
    rid = risk.get('id', '')
    num = id_to_num(rid)
    current_status = risk.get('status', 'open')

    if num not in UPDATES:
        # Closed risks not in UPDATES — preserve as-is
        continue

    new_score, signals, new_misses, status_override = UPDATES[num]
    old_score = risk.get('score', 0)
    old_status = current_status

    risk['score_last_run'] = old_score
    risk['score'] = new_score
    risk['signals'] = signals
    risk['consecutive_misses'] = new_misses

    if new_score > old_score:
        risk['score_trend'] = 'up'
    elif new_score < old_score:
        risk['score_trend'] = 'down'
    else:
        risk['score_trend'] = 'flat'

    risk['severity'] = severity_from_score(new_score)

    if status_override:
        risk['status'] = status_override
    elif new_score >= 6 and not risk.get('suppressed', False):
        risk['status'] = 'Escalated'
    elif old_status == 'Escalated' and new_score < 6:
        risk['status'] = 'open'
    # else: leave status unchanged

    new_status = risk['status']
    if old_score != new_score or old_status != new_status:
        changes.append(
            f"  {rid}: score {old_score}→{new_score} ({risk['score_trend']}) | "
            f"status {old_status}→{new_status}"
        )

print(f"\n=== CHANGES ({len(changes)}) ===")
for c in sorted(changes):
    print(c)

# Add RR-051
new_risk = {
    'id': 'RR-051',
    'title': 'PLAYER-1552 — SBClub login migration from iCore to Betler, scope risk',
    'status': 'open',
    'score': 1,
    'score_last_run': 0,
    'score_trend': 'up',
    'severity': 'low',
    'jira_issues': ['PLAYER-1552'],
    'planned_release_date': None,
    'signals': ['Slack-mention(1)'],
    'consecutive_misses': 0,
    'notion_page_id': None,
    'suppressed': False,
    'first_seen_run': RUN_NUMBER,
    'created': TODAY,
}
data['risks'].append(new_risk)
print(f"\nAdded RR-051: PLAYER-1552 SBClub login migration, score=1")

# Update SD-004 times_suggested → 3
for sd in data.get('suggested_dependencies', []):
    if sd.get('id') == 'SD-004':
        sd['times_suggested'] = 3
        sd['confidence_reason'] = (
            sd.get('confidence_reason', '')
            + ' Run 15 (2026-05-26): GAM-11319 still Blocked (Escalated, score=14).'
            ' GAM-10668 surfaced in #content-engagement-integrations-sync for third consecutive week.'
            ' Both remain highest-risk Bragg initiatives co-targeting May 29.'
        )
        print(f"Updated SD-004: times_suggested=3")

# Register metadata
data['run_number'] = RUN_NUMBER
data['last_run'] = TODAY
data['notion_sync_skipped_this_run'] = True
data['cpr_scan_skipped_this_run'] = True
data['notion_sync_skip_reason'] = 'HTTP 429 rate-limit on Notion API (retried once, still 429)'

with open(REGISTER_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nSaved: run {RUN_NUMBER}, {len(data['risks'])} risks, last_run={TODAY}")

# Quick validation
active = [r for r in data['risks'] if r.get('status') not in ('Closed',)]
escalated = [r for r in data['risks'] if r.get('status') == 'Escalated']
print(f"Active: {len(active)} | Escalated: {len(escalated)}")
for r in sorted(escalated, key=lambda x: -x.get('score', 0)):
    print(f"  {r['id']}: score={r['score']} suppressed={r.get('suppressed',False)} | {r.get('title','')[:60]}")
