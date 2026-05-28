#!/usr/bin/env python3
"""
register_utils.py — RO Risk Register CLI utility

Permanent project tool. Replaces ad-hoc update_register.py and finalize_register.py
scripts. All register read/write operations go through here.

Subcommands:
  summary           Print current register state overview
  notion-sync-plan  Show exactly which risks need Notion creates vs updates
  set-meta          Update top-level run metadata fields
  apply-scores      Apply a scores.json file of risk updates for a run
  finalize          Apply Notion page IDs, suppressed readback, comments, SD increments
  validate-fields   Assert all qualifying risks have notion_page_id set

Usage:
  python register_utils.py summary
  python register_utils.py notion-sync-plan
  python register_utils.py set-meta --run 17 --date 2026-05-28 [--notion-sync-done] [--slack-unavailable]
  python register_utils.py apply-scores --file scores.json
  python register_utils.py finalize --file finalize.json
  python register_utils.py validate-fields

scores.json format:
  {
    "run_number": 17, "generated": "ISO datetime",
    "risks": [
      {
        "id": "RR-002",         # required
        "score": 9,             # final amplified score; omit to leave unchanged
        "status": "Escalated",  # omit to leave unchanged
        "signals": [...],       # full replacement; omit to leave unchanged
        "slack_threads": [...], # full replacement; omit to leave unchanged
        "sources": [...],       # omit to leave unchanged
        "jira_issues": [...],   # omit to leave unchanged
        "planned_release_date": "2026-06-15",  # null = clear field; omit = leave unchanged
        "days_to_release": 24,  # omit to leave unchanged
        "product_lead": "...",  # null = clear; omit = leave unchanged
        "engineering_lead": null,
        "category": "...",
        "workstream": "...",
        "impact": "...",
        "epic_context": {...},  # null = clear; omit = leave unchanged
        "blockers": [...],
        "notes": "...",         # full replacement; omit = leave unchanged
        "new_this_run": false   # omit to let utility handle
      }
    ],
    "new_risks": [              # first-seen risks this run
      { "id": "RR-052", "title": "...", "score": 4, "category": "compliance",
        "workstream": "GAM", "jira_issues": [], "signals": [], "slack_threads": [],
        "sources": [], "status": "open", "impact": "medium",
        "planned_release_date": null, "days_to_release": null,
        "product_lead": null, "engineering_lead": null,
        "epic_context": null, "blockers": [], "notes": "" }
    ],
    "resolved_ids": [],        # risks explicitly NOT seen this run (misses incremented)
    "suggested_dependencies": [
      { "id": "SD-003", "action": "increment",
        "note": "Run 17 (2026-05-28): both co-occurring" }
      # action "new" requires full SD object fields
      # action "dismiss" requires dismissed_by string
    ],
    "meta": {                  # optional — overrides for top-level register fields
      "slack_unavailable_this_run": false,
      "dq_not_closed_out": []
    }
  }

finalize.json format:
  {
    "run_number": 17, "generated": "ISO datetime",
    "notion_page_ids": [
      { "id": "RR-033", "notion_page_id": "36e032f852c581bcb845e4bed560820f" }
    ],
    "suppressed_updates": [
      { "id": "RR-011", "suppressed": true, "suppressed_by": "notion-checkbox-run17" }
    ],
    "comments_posted": [
      { "risk_id": "RR-014", "jira_key": "PLAYER-11",
        "date": "2026-05-28", "run_number": 17, "comment_id": "1279306" }
    ],
    "sd_increments": [
      { "id": "SD-003", "times_suggested": 5 }   # absolute value, not delta
    ],
    "meta": {
      "last_run": "2026-05-28", "run_number": 17,
      "notion_sync_skipped_this_run": false,
      "dq_not_closed_out": []
    }
  }
"""
import sys, json, argparse, os
from datetime import date as Date

sys.stdout.reconfigure(encoding='utf-8')

REGISTER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'risk-register.json')
VALID_STATUSES  = {'open', 'Escalated', 'Resolved', 'Closed', 'Monitoring', 'Suppressed'}
SCORE_FIELDS    = ('score', 'status', 'signals', 'slack_threads', 'sources', 'jira_issues',
                   'planned_release_date', 'days_to_release', 'product_lead', 'engineering_lead',
                   'category', 'workstream', 'impact', 'epic_context', 'blockers', 'notes')


# ── I/O helpers ────────────────────────────────────────────────────────────────

def _load(path=None):
    with open(path or REGISTER, encoding='utf-8') as f:
        return json.load(f)


def _save(data, path=None):
    target = path or REGISTER
    tmp    = target + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, target)   # atomic rename


# ── Score helpers ───────────────────────────────────────────────────────────────

def _severity(score):
    if score >= 6: return 'high'
    if score >= 3: return 'medium'
    return 'low'


def _trend(new_score, old_score):
    if new_score > old_score: return 'up'
    if new_score < old_score: return 'down'
    return 'stable'


def _notion_trend(raw):
    return {'up': 'Worsening', 'down': 'Improving', 'stable': 'Stable',
            '↑': 'Worsening', '↓': 'Improving', '→': 'Stable'}.get(raw, 'Stable')


def _notion_status(raw):
    return 'Open' if raw == 'open' else str(raw)


# ── summary ────────────────────────────────────────────────────────────────────

def cmd_summary(args, data):
    risks = data.get('risks', [])
    by_status = {}
    for r in risks:
        by_status.setdefault(r.get('status', '?'), []).append(r)

    open_risks = [r for r in risks if r.get('status') not in ('Closed', 'Resolved')]
    sev = {}
    for r in open_risks:
        sev[r.get('severity', '?')] = sev.get(r.get('severity', '?'), 0) + 1

    print(f"=== Run {data.get('run_number')} | {data.get('last_run')} | {len(risks)} risks ===")
    status_line = '  '.join(f"{s}:{len(rs)}" for s, rs in sorted(by_status.items()))
    sev_line    = '  '.join(f"{s}:{c}" for s, c in sorted(sev.items()))
    print(f"Status:   {status_line}")
    print(f"Severity: {sev_line}  (open only)")

    dq_open = [r for r in open_risks if r.get('category') == 'data_quality']
    no_page = [r for r in open_risks
               if (r.get('severity') == 'high' or r.get('occurrences', 0) >= 2)
               and not r.get('notion_page_id')]
    new_risks = [r for r in risks if r.get('new_this_run')]
    print(f"DQ open:  {len(dq_open)}   New this run: {len(new_risks)}   Missing notion pages: {len(no_page)}")
    print(f"Notion sync skipped last run: {data.get('notion_sync_skipped_this_run', False)}")

    escalated = sorted([r for r in risks if r.get('status') == 'Escalated'],
                       key=lambda x: -x.get('score', 0))
    if escalated:
        print("\n--- ESCALATED ---")
        for r in escalated:
            jira = ', '.join(r.get('jira_issues', []) or [])
            print(f"  {r['id']} score={r.get('score')} trend={r.get('trend')} days={r.get('days_to_release')} | {jira}")
            print(f"    {r.get('title', '')[:72]}")

    if no_page:
        print("\n--- MISSING NOTION PAGE ---")
        for r in no_page:
            print(f"  {r['id']} sev={r.get('severity')} occ={r.get('occurrences')}")

    pend_sd = [s for s in data.get('suggested_dependencies', []) if s.get('status') == 'pending']
    if pend_sd:
        print("\n--- PENDING SUGGESTED DEPENDENCIES ---")
        for sd in pend_sd:
            print(f"  {sd['id']} ({sd['times_suggested']}x): {sd['initiative_a']} → {sd['initiative_b']}")


# ── notion-sync-plan ───────────────────────────────────────────────────────────

def cmd_notion_sync_plan(args, data):
    risks = data.get('risks', [])

    to_update, to_create = [], []
    for r in risks:
        pid    = r.get('notion_page_id')
        sev    = r.get('severity', 'low')
        occ    = r.get('occurrences', 0)
        status = r.get('status', '')
        if status in ('Closed', 'Resolved') and sev == 'low' and occ < 2:
            continue
        if sev == 'high' or status == 'Escalated' or sev == 'medium' or occ >= 2:
            (to_update if pid else to_create).append(r)

    print(f"=== NOTION SYNC PLAN — Run {data.get('run_number')} ===")
    print(f"DB: collection://7f410211-1a06-4fcc-b10c-ab58571a781a\n")

    print(f"UPDATE ({len(to_update)} existing pages):")
    for r in sorted(to_update, key=lambda x: -x.get('score', 0)):
        jira = ', '.join(r.get('jira_issues', []) or [])
        n_sev    = (r.get('severity') or 'low').capitalize()
        n_status = _notion_status(r.get('status', 'open'))
        n_trend  = _notion_trend(r.get('trend', 'stable'))
        signals  = ', '.join((r.get('signals') or [])[:3])
        slack_ev = '; '.join(t.get('summary', '')[:55] for t in (r.get('slack_threads') or [])[:2])
        print(f"  {r['id']} | page={r['notion_page_id']}")
        print(f"    Severity={n_sev}  Status={n_status}  Trend={n_trend}  Score={r.get('score')}  Days={r.get('days_to_release')}")
        print(f"    Jira={jira}")
        if signals:
            print(f"    Signals: {signals}")
        if slack_ev:
            print(f"    Slack: {slack_ev[:110]}")

    print(f"\nCREATE ({len(to_create)} new pages):")
    for r in sorted(to_create, key=lambda x: -x.get('score', 0)):
        jira     = ', '.join(r.get('jira_issues', []) or [])
        n_sev    = (r.get('severity') or 'low').capitalize()
        n_status = _notion_status(r.get('status', 'open'))
        n_trend  = _notion_trend(r.get('trend', 'stable'))
        signals  = ', '.join((r.get('signals') or [])[:3])
        slack_ev = '; '.join(t.get('summary', '')[:55] for t in (r.get('slack_threads') or [])[:2])
        print(f"  {r['id']} | sev={n_sev}  status={n_status}  trend={n_trend}  score={r.get('score')}  occ={r.get('occurrences')}  days={r.get('days_to_release')}")
        print(f"    Jira={jira}")
        print(f"    Title: {r.get('title', '')[:72]}")
        if signals:
            print(f"    Signals: {signals}")
        if slack_ev:
            print(f"    Slack: {slack_ev[:110]}")


# ── set-meta ───────────────────────────────────────────────────────────────────

def cmd_set_meta(args, data):
    if args.run is not None:
        data['run_number'] = int(args.run)
    if args.date:
        data['last_run'] = args.date
    if args.notion_sync_done:
        data['notion_sync_skipped_this_run'] = False
        data.pop('notion_sync_skip_reason', None)
    if args.slack_unavailable:
        data['slack_unavailable_this_run'] = True
    _save(data)
    print(f"Meta: run={data.get('run_number')}  last_run={data.get('last_run')}  "
          f"notion_sync_skipped={data.get('notion_sync_skipped_this_run')}")


# ── apply-scores ───────────────────────────────────────────────────────────────

def cmd_apply_scores(args, data):
    with open(args.file, encoding='utf-8') as f:
        scores = json.load(f)

    incoming_run = scores.get('run_number')
    current_run  = data.get('run_number')

    # Idempotency guard
    if incoming_run is not None and incoming_run == current_run:
        print(f"Already applied run {incoming_run} — skipping (idempotent).")
        return

    today = scores.get('generated', str(Date.today()))[:10]  # truncate to date part
    risks_by_id = {r['id']: r for r in data.get('risks', [])}

    updated, added, resolved = [], [], []

    # — update existing risks —
    for upd in scores.get('risks', []):
        rid = upd.get('id')
        r   = risks_by_id.get(rid)
        if r is None:
            print(f"  WARNING: {rid} not found in register — skipping update")
            continue

        old_score = r.get('score', 0)

        # Mandatory fields computed by utility
        if 'score' in upd:
            r['score_last_run'] = old_score
            r['score']          = upd['score']
            r['trend']          = _trend(upd['score'], old_score)
            r['severity']       = _severity(upd['score'])

        r['last_seen']          = today
        r['consecutive_misses'] = 0
        r['new_this_run']       = upd.get('new_this_run', False)

        # Only increment occurrences if not a brand-new risk
        if r.get('occurrences', 0) > 0:
            r['occurrences'] = r['occurrences'] + 1

        # Optional fields — apply only when explicitly included in update
        # null = clear the field; key absent = leave unchanged
        for field in SCORE_FIELDS:
            if field in upd and field not in ('score',):  # score already handled above
                r[field] = upd[field]

        # Guard: Closed → Escalated jump not allowed
        prev_status = risks_by_id.get(rid, {}).get('status', '')
        new_status  = upd.get('status', r.get('status', ''))
        if prev_status == 'Closed' and new_status == 'Escalated':
            print(f"  GUARD: {rid} cannot jump Closed→Escalated; setting to open instead")
            r['status'] = 'open'

        updated.append(rid)

    # — add new risks —
    for nr in scores.get('new_risks', []):
        rid = nr.get('id')
        if not rid:
            print(f"  WARNING: new_risk entry missing id field — skipping")
            continue
        if rid in risks_by_id:
            print(f"  WARNING: {rid} already exists in register — skipping new risk")
            continue
        new_score = nr.get('score', 0)
        new_r = {
            'id': rid,
            'comments_posted': [],
            'title': nr.get('title', ''),
            'category': nr.get('category', 'technical'),
            'sources': nr.get('sources', []),
            'signals': nr.get('signals', []),
            'slack_threads': nr.get('slack_threads', []),
            'score': new_score,
            'score_last_run': 0,
            'trend': 'new',
            'severity': _severity(new_score),
            'impact': nr.get('impact', 'medium'),
            'status': nr.get('status', 'open'),
            'workstream': nr.get('workstream', ''),
            'jira_issues': nr.get('jira_issues', []),
            'product_lead': nr.get('product_lead'),
            'engineering_lead': nr.get('engineering_lead'),
            'days_to_release': nr.get('days_to_release'),
            'planned_release_date': nr.get('planned_release_date'),
            'notion_page_id': None,
            'first_seen': today,
            'last_seen': today,
            'occurrences': 1,
            'consecutive_misses': 0,
            'new_this_run': True,
            'suppressed': False,
            'suppressed_by': None,
            'mitigation_action': nr.get('mitigation_action', ''),
            'mitigation_owner': nr.get('mitigation_owner', ''),
            'mitigation_target_date': None,
            'mitigation_status': 'none',
            'epic_context': nr.get('epic_context'),
            'blockers': nr.get('blockers', []),
            'notes': nr.get('notes', ''),
        }
        data['risks'].append(new_r)
        risks_by_id[rid] = new_r
        added.append(rid)

    # — handle explicit misses —
    seen_ids = {upd['id'] for upd in scores.get('risks', [])} | set(added)
    for rid in scores.get('resolved_ids', []):
        r = risks_by_id.get(rid)
        if r is None or r.get('status') == 'Closed':
            continue
        misses = r.get('consecutive_misses', 0) + 1
        r['consecutive_misses'] = misses
        r['new_this_run'] = False
        if misses >= 2:
            r['status']   = 'Closed'
            r['score']    = 0
            r['severity'] = 'low'
        elif misses == 1:
            r['status'] = 'Resolved'
        resolved.append(rid)

    # — suggested dependencies —
    sds_by_id = {s['id']: s for s in data.get('suggested_dependencies', [])}
    for sd_action in scores.get('suggested_dependencies', []):
        action = sd_action.get('action', 'increment')
        sid    = sd_action.get('id')
        if action == 'new':
            if sid and sid not in sds_by_id:
                new_sd = {k: v for k, v in sd_action.items() if k != 'action'}
                new_sd.setdefault('times_suggested', 1)
                new_sd.setdefault('status', 'pending')
                new_sd.setdefault('dismissed_by', None)
                data.setdefault('suggested_dependencies', []).append(new_sd)
        elif action == 'increment' and sid and sid in sds_by_id:
            sds_by_id[sid]['times_suggested'] = sds_by_id[sid].get('times_suggested', 0) + 1
            if 'note' in sd_action:
                sds_by_id[sid]['confidence_reason'] = (
                    sds_by_id[sid].get('confidence_reason', '').rstrip() + ' ' + sd_action['note']
                )
        elif action == 'dismiss' and sid and sid in sds_by_id:
            sds_by_id[sid]['status']       = 'dismissed'
            sds_by_id[sid]['dismissed_by'] = sd_action.get('dismissed_by', 'manual')

    # — meta —
    if incoming_run is not None:
        data['run_number'] = incoming_run
    data['last_run'] = today
    for k, v in scores.get('meta', {}).items():
        data[k] = v

    _save(data)
    print(f"apply-scores complete — run {incoming_run}:")
    print(f"  Updated: {len(updated)}  Added: {len(added)}  Resolved: {len(resolved)}")
    if added:
        print(f"  New IDs: {', '.join(added)}")
    if resolved:
        print(f"  Resolved: {', '.join(resolved)}")


# ── finalize ───────────────────────────────────────────────────────────────────

def cmd_finalize(args, data):
    with open(args.file, encoding='utf-8') as f:
        fin = json.load(f)

    risks_by_id = {r['id']: r for r in data.get('risks', [])}

    # Notion page IDs
    page_ids_set = 0
    for entry in fin.get('notion_page_ids', []):
        r = risks_by_id.get(entry.get('id'))
        if r and entry.get('notion_page_id'):
            r['notion_page_id'] = entry['notion_page_id']
            page_ids_set += 1

    # Suppressed readback
    suppressed_set = 0
    for entry in fin.get('suppressed_updates', []):
        r = risks_by_id.get(entry.get('id'))
        if r:
            r['suppressed']    = entry.get('suppressed', False)
            r['suppressed_by'] = entry.get('suppressed_by')
            suppressed_set += 1

    # Comments posted
    comments_added = 0
    for cp in fin.get('comments_posted', []):
        rid = cp.get('risk_id')
        if not rid:
            continue
        r = risks_by_id.get(rid)
        if not r:
            continue
        entry = {k: v for k, v in cp.items() if k != 'risk_id'}
        existing = r.get('comments_posted', [])
        cid = entry.get('comment_id')
        run = entry.get('run_number')
        if not any(c.get('comment_id') == cid and c.get('run_number') == run
                   for c in existing if cid):
            existing.append(entry)
            r['comments_posted'] = existing
            comments_added += 1

    # SD increments (absolute values from finalize.json)
    sds_by_id = {s['id']: s for s in data.get('suggested_dependencies', [])}
    sd_updated = 0
    for entry in fin.get('sd_increments', []):
        sid = entry.get('id')
        sd  = sds_by_id.get(sid)
        if sd and 'times_suggested' in entry:
            sd['times_suggested'] = entry['times_suggested']
            sd_updated += 1

    # Meta block
    for k, v in fin.get('meta', {}).items():
        data[k] = v

    _save(data)
    print(f"finalize complete:")
    print(f"  notion_page_ids set: {page_ids_set}")
    print(f"  suppressed flags:    {suppressed_set}")
    print(f"  comments_posted:     {comments_added}")
    print(f"  SD updates:          {sd_updated}")


# ── validate-fields ────────────────────────────────────────────────────────────

def cmd_validate_fields(args, data):
    risks   = data.get('risks', [])
    missing = []
    for r in risks:
        if r.get('status') in ('Closed', 'Resolved'):
            continue
        if r.get('severity') == 'high' or r.get('occurrences', 0) >= 2:
            if not r.get('notion_page_id'):
                missing.append(r['id'])

    with_pages = sum(1 for r in risks if r.get('notion_page_id'))
    if missing:
        print(f"FAIL: {len(missing)} qualifying risk(s) missing notion_page_id:")
        for rid in missing:
            r = next(x for x in risks if x['id'] == rid)
            print(f"  {rid}  sev={r.get('severity')}  occ={r.get('occurrences')}  status={r.get('status')}")
        sys.exit(1)
    else:
        print(f"OK: all qualifying risks have notion_page_id ({with_pages} total pages)")


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='RO Risk Register utility')
    sub    = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('summary',           help='Print register state overview')
    sub.add_parser('notion-sync-plan',  help='Show which risks need Notion creates/updates')
    sub.add_parser('validate-fields',   help='Assert all qualifying risks have notion_page_id')

    p_meta = sub.add_parser('set-meta', help='Update run metadata')
    p_meta.add_argument('--run',               type=int, help='Run number')
    p_meta.add_argument('--date',                        help='Run date YYYY-MM-DD')
    p_meta.add_argument('--notion-sync-done',  action='store_true')
    p_meta.add_argument('--slack-unavailable', action='store_true')

    p_scores = sub.add_parser('apply-scores', help='Apply scores.json to register')
    p_scores.add_argument('--file', required=True, help='Path to scores.json')

    p_fin = sub.add_parser('finalize', help='Apply finalize.json to register')
    p_fin.add_argument('--file', required=True, help='Path to finalize.json')

    args = parser.parse_args()
    data = _load()

    dispatch = {
        'summary':          cmd_summary,
        'notion-sync-plan': cmd_notion_sync_plan,
        'set-meta':         cmd_set_meta,
        'apply-scores':     cmd_apply_scores,
        'finalize':         cmd_finalize,
        'validate-fields':  cmd_validate_fields,
    }
    dispatch[args.cmd](args, data)


if __name__ == '__main__':
    main()
