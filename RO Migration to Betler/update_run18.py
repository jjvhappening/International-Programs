import sys, json
from datetime import date, datetime

sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = r'C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json'
TODAY = '2026-05-29'
TODAY_DATE = date(2026, 5, 29)

def calc_days(prd):
    if not prd:
        return None
    try:
        d = datetime.strptime(str(prd)[:10], '%Y-%m-%d').date()
        return (d - TODAY_DATE).days
    except:
        return None

def get_severity(score):
    if score >= 6:
        return 'high'
    elif score >= 3:
        return 'medium'
    else:
        return 'low'

def get_trend(new_score, old_score):
    if new_score > old_score:
        return 'up'
    elif new_score < old_score:
        return 'down'
    else:
        return 'stable'

with open(REGISTER_PATH, encoding='utf-8') as f:
    data = json.load(f)

risks = data['risks']
risk_map = {r['id']: r for r in risks}

def update_risk(rid, new_score, new_signals=None, new_slack_threads=None,
                new_status=None, note_append=None, new_epic_context=None):
    r = risk_map[rid]
    old_score = r.get('score', 0)
    r['score_last_run'] = old_score
    r['score'] = new_score
    r['trend'] = get_trend(new_score, old_score)
    r['severity'] = get_severity(new_score)
    r['new_this_run'] = False
    if new_status:
        r['status'] = new_status
    if new_signals is not None:
        r['signals'] = new_signals
    if new_slack_threads is not None:
        r['slack_threads'] = new_slack_threads
    if new_epic_context is not None:
        r['epic_context'] = new_epic_context
    if note_append:
        r['notes'] = (r.get('notes') or '') + ' ' + note_append
    r['occurrences'] = r.get('occurrences', 0) + 1
    if new_score > 0:
        r['last_seen'] = TODAY
        r['consecutive_misses'] = 0
    else:
        r['consecutive_misses'] = r.get('consecutive_misses', 0) + 1
    prd = r.get('planned_release_date')
    if prd:
        r['days_to_release'] = calc_days(prd)

# ── SPECIFIC RISK UPDATES ────────────────────────────────────────

# RR-002 PLAYER-1299 — score 9 stable; epic reclassified → in_progress_overdue, label must be REMOVED
update_risk('RR-002', 9,
    new_signals=["Slack-risk-language(2)", "Slack-regression-5+replies(3)", "Cross-source-bonus(2)"],
    new_slack_threads=[
        {"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860", "channel": "#ip-romania-discussions",
         "summary": "Regression test 2: Manage YELLOW, 2FA failures MANAGE-4169/MANAGE-4209 as highest-priority blockers"},
        {"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900", "channel": "#tmp-romania-migration-testing",
         "summary": "70 bugs found - Manage KYC area needs 2FA fixes before audit"}],
    new_epic_context={"classification": "in_progress_overdue", "label_stamped": False,
        "note": "Run 18: MANAGE-2996, MANAGE-3005, MANAGE-3006, MANAGE-3135 have In Progress epics. Not qualifying as not_closed_out. ro-not-closed-out label removed."},
    note_append="Run 18 (2026-05-29): Regression signals persistent. ro-not-closed-out label removed (epics In Progress).")

# RR-004 DAP-3 — score 4 stable
update_risk('RR-004', 4,
    new_signals=["Slack-risk-language(2)", "Jira-risk(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C09V3SK2936/p1779782779",
        "channel": "#tmp-romania-migration-data",
        "summary": "Payment Device QA gap - Karlo RED flag on data completeness"}])

# RR-005 PLAYER-1375 — score 2 stable (SEON signal still present)
update_risk('RR-005', 2,
    new_signals=["Slack-mention(1)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860",
        "channel": "#ip-romania-discussions",
        "summary": "FPT-300 SEON identity mismatch on login - must-fix before audit"}])

# RR-011 PLAYER-102 — score 0 (suppressed)
update_risk('RR-011', 0,
    new_signals=["Slack-mention(1)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C08FSV38EJK/p1779096785627009",
        "channel": "#content-engagement-integrations-sync",
        "summary": "Majid Rodriguez: EGT Digital buy bonus Descoped for Q2. No Q2 delivery."}])

# RR-013 PLAYER-1177 — score 0 (PRD arrived, FPT-245 In Review, DQ only)
update_risk('RR-013', 0,
    new_signals=[], new_slack_threads=[],
    new_epic_context={"classification": "in_progress_overdue"},
    note_append="Run 18 (2026-05-29): PRD arrived. FPT-233 Done, FPT-245 In Review. No active external signals.")

# RR-014 PLAYER-11 — score 11 → 12 (PRD Jun 12 = 14d, x2.0 amplifier)
update_risk('RR-014', 12,
    new_signals=["Slack-risk-language(2)", "Jira-risk(2)", "Cross-source-bonus(2)", "Timeline-amplifier-x2.0-PRD-Jun-12"],
    new_slack_threads=[
        {"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860", "channel": "#ip-romania-discussions",
         "summary": "Regression: FPT-300 SEON mismatch, FPT-301 card hash missing, FPT-303 device fingerprint missing — all must-fix for audit"},
        {"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900", "channel": "#tmp-romania-migration-testing",
         "summary": "Fraud area YELLOW - 3 critical FP signal gaps; PLAYER-1361 now Pending Certification (positive blocker progress)"}],
    note_append="Run 18 (2026-05-29): PLAYER-1361 now Pending Certification — blocker unblocking. FPT-300/301/303 regression still open. PRD Jun 12 = 14d, x2.0.")

# RR-016 SPORTS-562 — score 3 stable
update_risk('RR-016', 3,
    new_signals=["Slack-risk-language(2)", "Jira-risk(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C0AT1NCEBKQ/p1779779340",
        "channel": "#sports-romania-migration",
        "summary": "Sports regression: BET-7254 and BS-1590 bugs found, Android bet placement blocked"}])

# RR-017 GAM-8800 — score 10 → 0 (PRD arrived, positive staging)
update_risk('RR-017', 0,
    new_signals=[], new_slack_threads=[],
    new_status='open',
    note_append="Run 18 (2026-05-29): PRD arrived (May 29). Positive staging news. Score 10 → 0. Downgraded from Escalated to open.")

# RR-019 PLT-330 — score 1 → 3 (stage instability signals in regression context)
update_risk('RR-019', 3,
    new_signals=["Slack-risk-language(2)", "Jira-risk(2)"],
    new_slack_threads=[
        {"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860", "channel": "#ip-romania-discussions",
         "summary": "Stage instability signal from regression test 2 — platform dependency for multiple workstreams"},
        {"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900", "channel": "#tmp-romania-migration-testing",
         "summary": "Platform MIG environment issues flagged; EGT Buy Bonus still N/A on stage"}],
    note_append="Run 18 (2026-05-29): Stage instability signal from regression test 2. Score 1 → 3.")

# RR-021 PLAYER-218 — score 0 (no new signals)
update_risk('RR-021', 0, new_signals=[], new_slack_threads=[])

# RR-023 PLAYER-172 — score 8 → 0 (stale gone, no new external signals)
update_risk('RR-023', 0,
    new_signals=[], new_slack_threads=[],
    new_status='open',
    note_append="Run 18 (2026-05-29): PLAYER-172 freshly updated (stale=0). No new external signals. Score 8 → 0. Downgraded from Escalated. PRD Jun 1 = 3 days.")

# RR-029 GAM-10668 — score 14 → 2 (PRD arrived, suppressed, DQ signal only)
update_risk('RR-029', 2,
    new_signals=["Jira-risk(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C09UY82EE9L/p1779762050",
        "channel": "#tmp-romania-migration-gaming",
        "summary": "Playson stage sign-off pending; Bragg FS RO Nap still In Delivery on PRD day"}],
    new_status='open',
    note_append="Run 18 (2026-05-29): PRD arrived (May 29). Suppressed. Score 14 → 2.")

# RR-033 PLAYER-869 — score 1 stable (CICO Jun 3)
update_risk('RR-033', 1,
    new_signals=["Slack-mention(1)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C0590TS6NET/p1778833222584709",
        "channel": "#arcane-team",
        "summary": "CICO OTC Deposit targeting June 3; SBClub and Data team dependencies noted"}])

# RR-034 PLAYER-921 — score 1 stable
update_risk('RR-034', 1, new_signals=[], new_slack_threads=[])

# RR-035 PLAYER-1063 — score 5 stable (Transact regression)
update_risk('RR-035', 5,
    new_signals=["Jira-risk(2)", "Slack-risk-language(2)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860",
        "channel": "#ip-romania-discussions",
        "summary": "Transact YELLOW - TRX-2542 withdrawal tax wrong amount to Nuvei (Highest priority, In Progress)"}])

# RR-036 PLAYER-1064 — score 2 stable (Wallet regression)
update_risk('RR-036', 2,
    new_signals=["Jira-risk(2)", "Slack-risk-language(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900",
        "channel": "#tmp-romania-migration-testing",
        "summary": "Withdrawable amount inconsistent between Android and iOS/Web"}])

# RR-037 PLAYER-169 — score 5 stable (KYC regression)
update_risk('RR-037', 5,
    new_signals=["Slack-risk-language(2)", "Jira-risk(2)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779792860",
        "channel": "#ip-romania-discussions",
        "summary": "Manage YELLOW from regression - 2FA failures affecting KYC flows; audit starts next week, 21d to PRD"}])

# RR-039 GAM-11474 — score 2 stable (Playson contract risk, mitigated)
update_risk('RR-039', 2,
    new_signals=["Jira-risk(2)", "Slack-mention(1)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C09UY82EE9L/p1779762050",
        "channel": "#tmp-romania-migration-gaming",
        "summary": "Playson prod signed off on Hidden Production — contract risk mitigated; audit readiness ongoing"}],
    note_append="Run 18 (2026-05-29): PRD Jun 1 = 3d. Playson audit imminent.")

# RR-040 GAM-10782 — score 0 (PRD arrived, G.Games working on stage)
update_risk('RR-040', 0, new_signals=[], new_slack_threads=[],
    note_append="Run 18 (2026-05-29): PRD arrived (May 29). G.Games working on stage. Score = 0.")

# RR-041 GAM-11319 — score 14 stable (Spribe blocked+descoped, PRD today)
update_risk('RR-041', 14,
    new_signals=["Blocked-Status(3)", "Slack-risk-language(2)", "Cross-source-bonus(2)", "Timeline-amplifier-x2.0-PRD-May-29"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C08FSV38EJK/p1779758830",
        "channel": "#content-engagement-integrations-sync",
        "summary": "Spribe slow replies from Bragg - Day-1 risk; confirmed blocked+descoped, commercial resolution TBD"}],
    note_append="Run 18 (2026-05-29): PRD arrived (May 29). Still Blocked. Spribe confirmed blocked+descoped. Commercial resolution ongoing.")

# RR-042 GAM-10333 — score 2 → 4 (Playson commercial risk + PRD day DQ)
update_risk('RR-042', 4,
    new_signals=["Jira-risk(2)", "Slack-mention(1)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C09UY82EE9L/p1779762050",
        "channel": "#tmp-romana-migration-gaming",
        "summary": "Playson Direct Integration: stage sign-off still pending; commercial pressure on PRD day"}],
    note_append="Run 18 (2026-05-29): PRD arrived (May 29). Playson stage sign-off pending. Score 2 → 4.")

# RR-043 betslip ticket search — score 1 stable
update_risk('RR-043', 1,
    new_signals=["Slack-mention(1)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C088XJ978ES/p1778509485",
        "channel": "#ip-romania-discussions",
        "summary": "Niels: Online betslip ticket search 600k queries/month — scope confirmation needed"}])

# RR-044 PLAYER-105 — score 0 (no new signals)
update_risk('RR-044', 0, new_signals=[], new_slack_threads=[])

# RR-045 PLAYER-1425 — score 0 (no new signals)
update_risk('RR-045', 0, new_signals=[], new_slack_threads=[])

# RR-046 Pateplay jackpot — score 2 stable
update_risk('RR-046', 2,
    new_signals=["Slack-mention(1)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C09UY82EE9L/p1779762050",
        "channel": "#tmp-romania-migration-gaming",
        "summary": "Jackpot pots: 4 providers pending; Pateplay jackpot API tbd; Prag jackpot fails on stage"}])

# RR-047 SPORTS-1097 — score 1 stable
update_risk('RR-047', 1,
    new_signals=["Jira-risk(2)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C0AT1NCEBKQ/p1779622633",
        "channel": "#sports-romania-migration",
        "summary": "Stage cutover to Betler-only set Aug 10, pending refinement with Comtrade"}])

# RR-048 PLAYER-1070 — score 1 stable
update_risk('RR-048', 1, new_signals=["Slack-mention(1)"], new_slack_threads=[])

# RR-049 PLAYER-888 — score 5 stable (Nuvei/Transact)
update_risk('RR-049', 5,
    new_signals=["Jira-risk(2)", "Slack-risk-language(2)", "Cross-source-bonus(2)"],
    new_slack_threads=[{"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900",
        "channel": "#tmp-romania-migration-testing",
        "summary": "TRX-2542 withdrawal tax wrong amount to Nuvei (Highest priority); transaction history not loading"}])

# RR-051 PLAYER-1552 — score 1 → 0 (release was 2026-05-28)
update_risk('RR-051', 0, new_signals=[], new_slack_threads=[],
    note_append="Run 18 (2026-05-29): Release was 2026-05-28. Score → 0.")

# RR-052 Cert audit — score 4 → 12 (HIGH), status open → Escalated
r52 = risk_map['RR-052']
old_score_52 = r52.get('score', 0)
r52['score_last_run'] = old_score_52
r52['score'] = 12
r52['trend'] = 'up'
r52['severity'] = 'high'
r52['status'] = 'Escalated'
r52['last_seen'] = TODAY
r52['occurrences'] = r52.get('occurrences', 0) + 1
r52['consecutive_misses'] = 0
r52['new_this_run'] = False
r52['signals'] = ["Slack-risk-language(2)", "Jira-risk(2)", "Cross-source-bonus(2)", "Timeline-amplifier-x2.0-PRD-Jun-02"]
r52['slack_threads'] = [
    {"url": "https://superbet.slack.com/archives/C088XJ978ES/p1779734650", "channel": "#ip-romania-discussions",
     "summary": "Gabriel Popoiu: Audit starting next week — keep stage stable. 6 areas YELLOW from regression test 2."},
    {"url": "https://superbet.slack.com/archives/C0AR5US8NVB/p1779792900", "channel": "#tmp-romania-migration-testing",
     "summary": "70 bugs found across 6 YELLOW workstreams; certification audit milestone June 2 at risk"}]
r52['planned_release_date'] = "2026-06-02"
r52['days_to_release'] = calc_days("2026-06-02")
r52['sources'] = ["slack", "cpr"]
r52['category'] = "compliance"
r52['jira_issues'] = r52.get('jira_issues', [])
r52['suppressed'] = False
r52['epic_context'] = None
if not r52.get('notion_page_id'):
    r52['notion_page_id'] = None
r52['first_seen'] = r52.get('first_seen', '2026-05-28')
r52['workstream'] = r52.get('workstream', 'CROSS')
r52['comments_posted'] = r52.get('comments_posted', [])
r52['notes'] = (r52.get('notes') or '') + " Run 18 (2026-05-29): Audit confirmed starting ~Jun 2. Stage instability: 70 bugs, 6 YELLOW areas. Score 4 → 12 (HIGH). Status → Escalated."

# ── UNCHANGED OPEN RISKS (metadata sweep only) ──────────────────
UNCHANGED_IDS = ['RR-012', 'RR-015', 'RR-020', 'RR-022', 'RR-024', 'RR-025', 'RR-027', 'RR-028',
                 'RR-030', 'RR-031', 'RR-032', 'RR-038']
for rid in UNCHANGED_IDS:
    if rid not in risk_map:
        continue
    r = risk_map[rid]
    if r.get('status', 'open') in ['Closed', 'Resolved']:
        continue
    old_score = r.get('score', 0)
    r['score_last_run'] = old_score
    r['new_this_run'] = False
    r['occurrences'] = r.get('occurrences', 0) + 1
    if old_score > 0:
        r['last_seen'] = TODAY
        r['consecutive_misses'] = 0
    else:
        r['consecutive_misses'] = r.get('consecutive_misses', 0) + 1
    prd = r.get('planned_release_date')
    if prd:
        r['days_to_release'] = calc_days(prd)
    r['trend'] = '→'

# ── TOP-LEVEL METADATA ───────────────────────────────────────────
data['run_number'] = 18
data['last_run'] = TODAY
data['slack_unavailable_this_run'] = False
data['notion_sync_skipped_this_run'] = False  # will update below if needed
data['dq_not_closed_out'] = []  # PLAYER-1299 removed; no new not_closed_out this run
data['meta'] = {
    'run_number': 18,
    'last_run': TODAY,
    'last_run_risks': len([r for r in risks if r.get('status', 'open') not in ['Closed', 'Resolved']]),
    'total_risks': len(risks)
}

with open(REGISTER_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Summary
escalated = [r for r in risks if r.get('status') == 'Escalated']
active = [r for r in risks if r.get('status', 'open') not in ['Closed', 'Resolved']]
high_severity = [r for r in risks if r.get('severity') == 'high' and r.get('status') not in ['Closed', 'Resolved']]

print(f"Run 18 register written.")
print(f"Total risks: {len(risks)}")
print(f"Active: {len(active)}")
print(f"Escalated: {len(escalated)} — {[r['id'] for r in escalated]}")
print(f"High severity: {len(high_severity)} — {[r['id'] for r in high_severity]}")
print()
print("=== KEY SCORE CHANGES ===")
key_ids = ['RR-002', 'RR-014', 'RR-017', 'RR-019', 'RR-023', 'RR-029', 'RR-041', 'RR-042', 'RR-052']
for rid in key_ids:
    r = risk_map[rid]
    print(f"  {rid}: {r.get('score_last_run')} → {r.get('score')} ({r.get('trend')}) | {r.get('status')} | {r.get('severity')}")
