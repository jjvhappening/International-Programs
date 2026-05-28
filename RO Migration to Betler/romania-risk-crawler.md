# Romania Risk Crawler (PLYRTPM-33)

## Objective
Build a weekly automated routine that scans across Jira, Slack, and CPR sources to identify topics that are at risk or generating high discussion, then surfaces findings as a Slack digest to `#ro-migration-risks` and auto-comments on stale Jira issues.

---

## Phase 0 — Load tools (run once at session start)

Before any data collection begins, load all required tool schemas in two batches. Do not proceed to Phase 1 until all tools are confirmed loaded.

```
ToolSearch: select:mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__searchJiraIssuesUsingJql,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__getJiraIssue,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__addCommentToJiraIssue,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__getTransitionsForJiraIssue,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__transitionJiraIssue,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__editJiraIssue
```

```
ToolSearch: select:mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-fetch,mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-query-data-sources,mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-update-page,mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-create-pages,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_send_message,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_read_thread,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_search_public_and_private
```

Also read these reference files before Phase 1 to avoid runtime lookup round-trips:
- Notion schema: `C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\references\notion-risk-register-schema.md`
- Slack channel IDs: `C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\references\slack-channels.md`
- Risk register: `C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\risk-register.json`

Verify permanent utilities are present (do not delete these between runs):
- `C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\register_utils.py`
- `C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler\jira_extract.py`

---

## Data Sources

| Source | What to scan |
|---|---|
| **Jira** | All Romania migration initiatives across all boards. **JQL**: `project in (IP,PLAYER,GAM,DAP,PLT,SOC,SPORTS) AND text ~ "Romania" AND issuetype = Initiative AND status NOT IN (Backlog, "Won't Do") ORDER BY updated DESC`. ⚠️ `cf[14342] = "🇷🇴 Romania migration"` does **NOT** work — the emoji-prefixed multi-select field returns 0 results with `cf[]` equality; `text ~ "Romania"` is the confirmed working alternative. As of 2026-05-01: **200+ initiatives** across IP (113), PLAYER (75), GAM (5), DAP (4), PLT (2), SOC (1). Query must paginate — results exceed 100 per page. PLYRTPM is not in scope — it tracks Jon's TPM tasks, not program deliverables. |
| **Slack** | All channels whose name contains `romania` or `ip` (including temp channels) |
| **Notion** | CPR session pages across all P&T areas (see CPR Database Inventory below) |

---

## Notion CPR Database Inventory

| Area | Notion Resource | Collection ID / Notes |
|---|---|---|
| **Player** | [Player CPR Database](https://www.notion.so/superbet/Player-CPR-Database-188032f852c58040967dd8de7c54b724) | `collection://188032f8-52c5-8000-b7f6-000b00643df3` — main CPRs collection |
| Player (supporting) | Player Escalation and Risks DB | `collection://1d5032f8-52c5-80df-968b-000b2eab97df` |
| Player (supporting) | Player Action Items and Follow-Ups DB | `collection://1d5032f8-52c5-800e-bb9b-000b0d0c933d` |
| **Sports** | [Sports Tribes CPRs](https://app.notion.com/p/11a032f852c580e2907ee5d654bd0790) | Shared database across all Sports tribes |
| **Social** | [Social Jira CPR Database](https://app.notion.com/p/1de032f852c580d8bb0dc397c05edfbf) | `collection://1de032f8-52c5-8019-8992-000b77887557` — has direct `CPR Health` + `CPR Health Update` fields; can query directly |
| **Fraud Prevention** | Individual CPR session pages | No single database page found — scan by page title pattern `CPR Fraud Prevention` |
| **Multichannel** | Individual CPR session pages | Scan by title pattern `Multichannel CPR` |
| **Transact** | Individual CPR session pages | Scan by title pattern `Transact CPR` — note: contains RO Migration tracking |
| **Engagement** | Individual CPR session pages | Scan by title pattern `Engagement CPR` |
| **Onboarding/Identity** | Individual CPR session pages | Scan by title pattern `CPR Template (Onboarding, Identity)` |

---

## Signal Logic

### 1. Jira signals

Field IDs from [Jira Roadmap Logic v2](../../Jira%20Data%20Quality/references/Jira%20Roadmap%20Logic%20v2.md).

| Signal | Field / Definition | Weight |
|---|---|---|
| Health Status = Red | `customfield_12111` value contains `"off track"` (e.g. `"🔴 Off Track"`) | 4 |
| Health Status = Amber | `customfield_12111` value contains `"at risk"` (e.g. `"🟡 At Risk"`) | 2 |
| Flagged | Issue has the Jira "flagged" marker | 3 |
| Blocked / at-risk | Status = Blocked, or label includes `at-risk` | 3 |
| Short Status Update contains risk language | `customfield_14447` contains "blocked" / "at risk" / "delayed" / "dependency" | 2 |
| Stale — in delivery | Status in (In Planning, In Delivery, In Production) with no comment or field update in **7 days** | 2 |
| `is blocked by` dependency flagged | Linked issue (via Jira issue links) is Blocked, flagged, or stale | 2 |
| Planned Release Date overdue — backlog (genuine risk) | `customfield_12114` past AND all child epics are in Backlog / To Do (work not yet started) | 3 |
| Planned Release Date overdue — in progress (data quality) | `customfield_12114` past AND at least one child epic is actively In Progress / In Delivery | 0 ¹ |
| *Planned Release Date slipped (rows below)* | *Scored only when all child epics are in Backlog / To Do — see [Epic Context Check](#epic-context-check). If any epic is In Progress / In Delivery, score 0 regardless of slip magnitude.* | — |
| Planned Release Date slipped — <1 week | Date changed vs prior run AND prior date was ≤7 days away | 4 |
| Planned Release Date slipped — <2 weeks | Date changed vs prior run AND prior date was 8–14 days away | 3 |
| Planned Release Date slipped — <3 weeks | Date changed vs prior run AND prior date was 15–21 days away | 2 |
| Planned Release Date slipped — <4 weeks | Date changed vs prior run AND prior date was 22–28 days away | 1 |
| Planned Release Date slipped — 4+ weeks | Date changed vs prior run AND prior date was >28 days away | 1 |
| Planned Release Date slipped — epics in progress (no score) | Date changed vs prior run AND at least one child epic is In Progress / In Delivery | 0 ¹ |
| Stale — pre-delivery | Status in (To Do, In Discovery, In Definition) with no update in **14 days** | 1 |
| Stale — backlog | Backlog with no update in **30 days** and activity detected in Slack/CPR | 1 |
| Health Status missing (in-delivery) | `customfield_12111` empty for initiative in Tier 4 status | 1 |
| Missing required fields | Planned Release Date (`customfield_12114`) or other Tier 4 required fields absent | 1 |
| No Jira data, external signal | Topic in Slack/CPR with no matching initiative found, or initiative with no description/comments | 1 |

> ¹ Score 0 — data quality signal only. Record in register as DQ; do not score as programme risk. See Epic Context Check below.

> **Planned Release Date overdue / slipped** — always uses `customfield_12114`, never the native Jira `duedate`. Classification (genuine risk vs data quality) is determined by the Epic Context Check below. **Slip detection**: compare `customfield_12114` against `planned_release_date` stored from the prior run; weights per table above. Inward pulls (date moved earlier) are noted but not scored. The `planned_release_date` field in the register is updated to the current value only after the full scoring pass completes — never incrementally — so a partial-run failure leaves all prior-run values intact for the next run.

> Status tier definitions follow the PLAYER status workflow: Pre-Delivery (Backlog → Awaiting Approval), Delivery (Awaiting Delivery → In Production), Post-Delivery (Rollout / Experimentation → In Cleanup). See Jira Roadmap Logic v2 for full workflow reference.

---

### Epic Context Check

Triggered for any initiative where the Planned Release Date (`customfield_12114`) has passed but the initiative is still in a delivery status. The crawler fetches all child epics of the initiative and classifies the signal:

**CRITICAL**: Fetch and examine EVERY child epic via JQL before classifying. A partial list can produce a wrong classification — do not classify until all epics are retrieved. Apply in priority order:

| Priority | Epic state | Classification | Action |
|---|---|---|---|
| 1 | One or more child epics In Progress / In Delivery (regardless of others) | `in_progress_overdue` — **data quality** | Score 0 for risk; delivery is underway — date needs updating but this is DQ, not risk |
| 2 | ALL child epics Done or Won't Do — zero exceptions, every epic checked | `not_closed_out` — **data quality** | Score 0 for risk; flag as DQ; stamp `ro-not-closed-out` label on PLAYER initiatives |
| 3 | Mix of Done/Won't Do + Backlog/To Do (some complete, some not yet started, none In Progress) | `partial_delivery` — **data quality** | Score 0 for risk; record as DQ; partial completion with unstarted work remaining |
| 4 | All child epics in Backlog / To Do (none started, none Done) | `backlog_overdue` — **genuine risk** | Apply `release_date_overdue` signal at full weight (3); treat as timeline risk |
| 5 | No child epics found | `no_epic_data` — **insufficient data** | Apply signal at weight 1; flag for investigation |

**Data quality issues** (`not_closed_out`, `in_progress_overdue`, `partial_delivery`) are written to the risk register with `category = "data_quality"` and surfaced in the 🗂 DQ section of the digest. They do not contribute to risk severity scoring and do not appear in the Escalated or Top 3 sections. Staleness signals on a DQ-category entry are still scored independently (a stale DQ entry still needs attention).

**SSU false positive guard:** if the Short Status Update contains risk-language keywords (blocked, at risk, delayed) but the phrase is preceded by a negation within 3 words (e.g. "no blockers", "not blocked", "not at risk"), the SSU signal is suppressed for that initiative.

### 2. Slack signals
| Signal | Definition | Weight |
|---|---|---|
| Risk emoji | Message contains ⚠️, 🚨, or the word "risk" / "blocked" / "escalate" | 2 |
| High discussion | Thread with **5+ replies in the last 7 days** | 3 |
| Unresolved thread | Thread older than 3 days with no resolution marker (e.g. ✅) | 2 |
| Single mention | Any message referencing an in-scope initiative name (minimum threshold) | 1 |

### 3. CPR signals (via Notion)

Signals from **structured databases** (Player, Social, Sports) carry full weight. Signals from **unstructured pages** (Fraud Prevention, Multichannel, Transact, Engagement, Onboarding/Identity) carry reduced weight — Jira cross-referencing is still attempted but matches are flagged as low-confidence.

| Signal | Source type | Weight |
|---|---|---|
| CPR Health = at-risk | Structured DB (Social) — direct `CPR Health` field | 3 |
| Recurring topic (2+ consecutive meetings) | Structured DB | 3 |
| Recurring topic (2+ consecutive meetings) | Unstructured pages | 1 |
| No resolution noted on agenda item | Structured DB | 2 |
| No resolution noted on agenda item | Unstructured pages | 1 |
| Single CPR mention | Any | 1 |

---

## Workstreams

Risks are grouped for digest and rollup by the Jira board of the linked initiative. Current program workstreams:

| Workstream | Jira Board | Initiatives (as of 2026-05-01) | Description |
|---|---|---|---|
| International Programs | IP | 113 | Main program delivery board — all feature/capability deliverables for the RO migration |
| Player | PLAYER | 75 | Player product initiatives tagged to the program — cross-audited by the Jira Data Quality workflow |
| Gaming | GAM | 5 | Gaming integrations — SB RO integrations, game provider integrations |
| Data & Analytics | DAP | 4 | Data migration, CRM data, analytics re-platforming |
| Platform | PLT | 2 | Platform-level initiatives supporting the migration |
| Social | SOC | 1 | Social product initiative tagged to the program |

External dependencies (e.g. Betler platform, payment providers, regulatory bodies) are not tracked via the crawler — they are added manually to the Notion risk register.

Jira Advanced Roadmap plan: [RO Migration timeline](https://axilis.atlassian.net/jira/plans/6282/scenarios/6417/timeline)

---

## Cross-Reference Logic
- **Jira stale + Slack active**: Jira issue has no update in 7 days BUT the topic is being actively discussed in Slack → **high priority flag** (data is out of date vs reality)
- **Slack risk signal + no Jira issue**: Something flagged in Slack with no corresponding Jira tracking → **create/flag for manual review**
- **CPR recurring + Jira not progressed**: Topic raised in multiple CPRs but Jira status unchanged → **escalation candidate**

---

## Dependency Inference

When two or more in-scope initiatives appear together in the same evidence — same Slack thread, same CPR agenda item, or an explicit dependency phrase connecting them — the crawler assesses whether a formal Jira link is missing and should be suggested.

### High confidence threshold

A suggestion is only surfaced when **all** of the following are true:

1. **Co-occurrence signal**: both initiative names appear in the same Slack thread OR the same CPR agenda item (same-channel-only does not qualify)
2. **No existing link**: Jira confirms no `is blocked by`, `blocks`, or `relates to` link already exists between the two initiatives
3. **Claude confirms**: Claude assesses the pair — given their summaries, categories, and the shared signal context — and concludes a dependency relationship is plausible with high confidence (explicit reasoning required; vague topical overlap does not qualify)

Suggestions that do not meet all three criteria are discarded silently — they do not appear in the digest or the register.

### Confidence boosters (any one raises confidence further)

- Explicit dependency language in the co-occurrence signal: "waiting for", "blocked by", "depends on", "before X we need Y", "can't proceed until"
- One initiative is stale while the other has active Slack discussion — suggesting one is waiting on the other
- Both initiatives share the same Product Lead or Engineering Lead

### Suggested dependency object (stored in `suggested_dependencies` in JSON)

```json
{
  "id": "SD-001",
  "initiative_a": "IP-45",
  "initiative_b": "IP-62",
  "suggested_link": "IP-45 is blocked by IP-62",
  "confidence_reason": "Both named in same #ro-ip-temp thread (2026-04-28): 'wallet must be live before registration can complete'",
  "first_suggested": "ISO date",
  "times_suggested": 1,
  "status": "pending",
  "dismissed_by": null
}
```

| Field | Description |
|---|---|
| `suggested_link` | Proposed Jira link direction — always phrased as "A is blocked by B" or "A blocks B" |
| `confidence_reason` | Quoted evidence: the specific thread, message, or CPR item that triggered the suggestion |
| `times_suggested` | Number of runs this pair has co-occurred; re-suggested after 3 runs of new evidence even if previously dismissed |
| `status` | `pending` / `accepted` / `dismissed` |
| `dismissed_by` | Name of person who dismissed (Jon, Niels, or an initiative lead) |

### In the digest

Suggestions appear in a dedicated section, clearly separated from confirmed risks:

```
🔗 *Suggested dependencies — review required*
• SD-001: IP-45 → IP-62
  "wallet must be live before registration can complete" — #ro-ip-temp (28 Apr)
  Suggested link: IP-45 is blocked by IP-62 | Accept (create Jira link) or Dismiss
```

Accepted suggestions are not acted on automatically — the programme lead creates the Jira link manually. On the next run the crawler picks up the formal link and handles it through normal dependency tracking.

---

## Outputs

### A. Daily Slack Digest → `#ro-migration-risks`
Posted every **weekday at 09:00 GMT**.
@mentioned: **Niels De Winde** (`U04MM3C1H8U`) and **Jon Vince** (`U08HBGPPRNY`) (additional recipients to be added later).

Format:
```
🔍 *RO Migration — Risk Digest* — [date] · [X] open · H:[N] M:[N] L:[N] · [N] resolved · <https://app.notion.com/p/9dab74b2885b4f8f93aa73dad97ea6da|Full register>
cc @niels.dewinde @jon.vince

🚨 *Escalated*
• [trend] <notion_url|RR-007> *Topic* — <jira_url|IP-45> · Stale 7d · Slack (8🧵) <thread_url|🧵> · 📅 12d · 🛠 In Progress

⚠️ *Top 5 risks*
• [trend] <notion_url|RR-012> *Topic* — <jira_url|IP-62> · Health🔴 · SSU · 📅 28d
• [trend] <notion_url|RR-015> *Topic* — <jira_url|GAM-8800> · Slack unresolved <thread_url|🧵> · Stale
• [trend] <notion_url|RR-018> *Topic* — no Jira · Slack (12🧵) <thread_url|🧵> · needs triage
_+N more in Notion_

🔗 *Suggested dependencies* — <notion_url|SD-001>: <jira_url|IP-45> → <jira_url|IP-62> · <notion_url|SD-002>: <jira_url|GAM-8800> → <jira_url|DAP-3>

✅ *Resolved* — <notion_url|RR-009> Topic

🗂 *DQ* — <jira_url|PLAYER-172> release 31 Mar, all epics Done · <jira_url|PLAYER-218> work complete, not closed

📊 PLT H:[N] M:[N] · PLAYER H:[N] M:[N] L:[N] · IP H:[N] · DAP H:[N] M:[N] · GAM — · SOC —

_🆕 new · ↑ worsening · → stable · ↓ improving · 📅 days to release (≤60d only) · 💬 Jira comment posted this run_
```

**Linking rules:**
- Every `RR-NNN` ID is hyperlinked to its Notion page: `<https://app.notion.com/p/[notion_page_id_no_dashes]|RR-NNN>`. If `notion_page_id` is null (risk not yet synced), render as plain `RR-NNN`.
- Every Jira issue key is hyperlinked: `<https://axilis.atlassian.net/browse/[KEY]|KEY>`.
- The header Notion link always points to the full register: `https://app.notion.com/p/9dab74b2885b4f8f93aa73dad97ea6da`.
- Suggested dependency IDs (SD-NNN) are not separately linked — the Jira keys within each suggestion are already linked.
- **Slack thread evidence**: when a risk has entries in `slack_threads`, append each as `<url|🧵>` immediately after the signal tag that the thread supports (e.g. after `Slack unresolved` or `Slack (N🧵)`). If multiple threads, chain them: `<url1|🧵> <url2|🧵>`. Thread URLs are read directly from `slack_threads[].url` in the JSON register — no Slack API call is needed at digest time.

**Digest rules:**
- Header is a single line: date, open count, H/M/L breakdown, resolved count, Notion link.
- Sections use emoji + bold heading inline — no separator bars.
- **One line per risk.** Signals abbreviated as tags: `Health🔴`, `Health🟡`, `SSU`, `Slack (N🧵)`, `CPR`, `Stale`, `Overdue`, `DateSlip`, `No Jira`. Omit tags not triggered.
- `💬` appended at the end of any risk line where `comments_posted` contains an entry with `run_number` equal to the current run. Omit if no entry for this run exists.
- `📅 Nd` only shown when Planned Release Date (`customfield_12114`) is set and within 60 days. Negative values shown as `📅 -Nd overdue`.
- `🛠 [status]` appended when `mitigation_status` is `planned` or `in_progress`.
- Trend prefix: `🆕` for `new_this_run = true`; `↑` / `→` / `↓` for recurring risks.
- **Escalated section** always shown; if none, render as `🚨 *Escalated* — none`.
- **Top 5** shows highest-scoring non-Escalated risks; `_+N more in Notion_` when total open > 5 + escalated count.
- **Resolved section** omitted entirely if no risks resolved this run.
- **DQ section** omitted entirely if no `data_quality` category entries are open this run (covers `not_closed_out`, `in_progress_overdue`, and `partial_delivery` classifications).
- **Suggested dependencies** section omitted if `suggested_dependencies` array is empty.
- Workstream summary always shown on one line; use `—` for workstreams with zero risks.

### B. Auto-comment on Jira issues

**Trigger rules — all require at least one corroborating external signal. Staleness alone never triggers a comment.**

| Trigger | Condition |
|---|---|
| Stale + external signal | Initiative is stale (7+ days in delivery, 14+ days pre-delivery) AND has a Slack thread or CPR mention this run |
| SSU risk language | SSU contains explicit risk keywords (blocked / at risk / delayed) — negation guard applied |
| No Jira match | External signal (Slack or CPR) references an in-scope topic but no matching initiative found — triage request |

**False positive guards:**
- Staleness alone → scored only, never commented
- SSU with negation within 3 words ("no blockers", "not at risk") → suppressed
- Health Status = Green with no external signal → no comment regardless of staleness

Comment template:
```
🤖 *[Initiative summary — one short sentence describing what this initiative delivers]*

Could you drop a quick update on the Short Status Update field? We're missing [specific field(s) — e.g. a status update / a planned release date] for this one.

We track RO Migration initiative health weekly — keeping this field current helps the programme team stay on top of any blockers early. Thanks!
```

**Template rules:**
- Line 1: one sentence stating what **this specific initiative** delivers — taken from the Jira summary of the issue being commented on. Do not copy the ticket title verbatim if it is cryptic; rephrase plainly.
- Line 2: name the specific field(s) that triggered the signal for **this issue** (e.g. "a status update", "a planned release date", "a health status"). Do not list signal codes or weights.
- Line 3: fixed closing line — always the same, friendly, not passive-aggressive.
- **Never reference other Jira keys in the comment body.** If a risk entry covers multiple initiatives (e.g. a grouped risk like RR-015), each auto-comment is scoped entirely to the initiative it is posted on. The recipient has no context for other tickets and cross-referencing them is confusing.
- Do not use words like "flagged", "risk scan", "stale", "overdue", or "no update in X days" — these read as accusatory.
- Do not comment on the same issue more than once per run.

---

## Implementation Approach

This will be built as a **Claude Code scheduled routine** using the `schedule` skill, running weekly.

### Sub-agent architecture

The crawl uses three parallel sub-agents for data collection. All raw API payloads, intermediate tool responses, and per-signal reasoning are contained within sub-agent context windows — none reach the main session. The main session handles register management and synthesis only.

**Launch sequence**

**Phase 1 (main session):** Load register + Notion suppressed flags (Step 1a). Read `risk-register.json` and note current `run_number` (N) and `last_run` date.

**Phase 2 (parallel launch):** Launch Jira and Notion collectors simultaneously using the `Agent` tool:

```
Agent(
  subagent_type="claude",
  description="Jira collector — Run N",
  prompt=<JIRA_COLLECTOR_PROMPT from Sub-Agent Prompt Templates appendix>,
  run_in_background=True
)

Agent(
  subagent_type="claude",
  description="Notion CPR collector — Run N",
  prompt=<NOTION_COLLECTOR_PROMPT from Sub-Agent Prompt Templates appendix>,
  run_in_background=True
)
```

Both prompts must have `run_number`, `last_run_date`, and the absolute path to `risk-register.json` substituted in before dispatch.

**Phase 3 (after Jira collector notifies complete):** Verify `references/jira-name-index-temp.json` exists and its `run_number` matches N. Then launch Slack collector (foreground — it needs the name index):

```
Agent(
  subagent_type="claude",
  description="Slack collector — Run N",
  prompt=<SLACK_COLLECTOR_PROMPT from Sub-Agent Prompt Templates appendix>,
  run_in_background=False
)
```

**Phase 4 (main session):** Once all three sub-agents have written their temp files, read `references/jira-signals-temp.json`, `references/slack-signals-temp.json`, `references/notion-signals-temp.json`. Verify `run_number` matches N in each. If any is missing or stale, abort and re-launch the failed sub-agent before proceeding. Continue with Steps 6–12.

**Sub-agent responsibilities**

| Sub-agent | Steps | Writes to disk |
|---|---|---|
| Jira collector | 1, 1b, 1c, 1d | `references/jira-signals-temp.json`, `references/jira-name-index-temp.json` |
| Notion collector | 5 | `references/notion-signals-temp.json` |
| Slack collector | 2, 4, 4b | `references/slack-signals-temp.json`; also edits `references/slack-channels.md` in-place via Step 4b |

**Sub-agent inputs (pass in prompt)**
- All three: `run_number`, `last_run_date`, absolute path to `risk-register.json` (sub-agents read prior state for slip detection and the one-comment-per-run guard)
- Slack collector only: absolute path to `references/jira-name-index-temp.json` (written by Jira collector; used to match Slack topic mentions to initiative keys)

**Sub-agent output file format**

```json
{
  "run_number": 12,
  "generated": "ISO datetime",
  "signals": [
    {
      "key": "IP-45",
      "sources": ["jira"],
      "signals": ["stale_7d", "health_red"],
      "score_contribution": 6,
      "days_to_release": 18,
      "planned_release_date": "2026-06-01",
      "product_lead": "Jane Smith",
      "engineering_lead": "John Doe",
      "epic_context": { "classification": "backlog_overdue", "active_epics": [], "done_epics": 3, "wont_do_epics": 0 },
      "slack_threads": [],
      "label_actions": [],
      "notes": ""
    }
  ]
}
```

**Temp file lifecycle**: temp files are overwritten at the start of each run and are not persisted between runs. Before consuming a temp file, check that `run_number` matches the current run — if it does not, the sub-agent failed silently and the main session must abort and re-launch that sub-agent.

### Context management

The sub-agent architecture is the primary protection against context saturation — raw API payloads never reach the main session. Within each sub-agent:

- Discard raw API payloads immediately after field extraction. Never retain the full JSON response in the sub-agent's context.
- For Jira responses > 50k characters: extract key, summary, status, updated, and relevant custom fields using PowerShell `ConvertFrom-Json` into a reduced array before processing in-context.
- At the end of processing, write the output file to disk and return a one-line summary only (e.g. `"Jira collector complete: 200 initiatives scanned, 14 signals written to jira-signals-temp.json"`). The full signal list travels via the output file, not via the return value — this keeps the main session's context footprint proportional to the number of signals, not the volume of raw data.

### Steps to build:
1a. **Load risk register** — read `risk-register.json` at the start of each run (create empty register if first run). For every risk where `notion_page_id` is set, read the Notion `Suppressed` checkbox and update `suppressed` in the JSON before scoring begins — this ensures suppressed risks are excluded from scoring, auto-comments, and digest output from the very first step.
1. **Define Jira scope query** — fetch all in-scope initiatives across all boards using: `project in (IP,PLAYER,GAM,DAP,PLT,SOC,SPORTS) AND text ~ "Romania" AND issuetype = Initiative AND status NOT IN (Backlog, "Won't Do") ORDER BY updated DESC`. ⚠️ Do NOT use `cf[14342] = "🇷🇴 Romania migration"` — confirmed non-functional across multiple runs (returns 0 results); the custom field is an emoji-prefixed multi-select that does not respond to `cf[]` equality filtering. **Request only these fields** (pass as `fields` parameter to avoid full-payload responses): `key,summary,status,updated,parent,customfield_12111,customfield_14447,customfield_12114,customfield_12121,customfield_12122,issuelinks,created,priority`. **Must paginate** — results exceed 100 (200 total as of 2026-05-01); fetch pages until `isLast = true`. Build a name index (`{ initiative_name → key, board, status }`) for Slack cross-referencing. Discard raw response after building the index. PLYRTPM is not in scope — do not query it. Immediately write the name index to `references/jira-name-index-temp.json` in this format: `{ "run_number": N, "generated": "ISO datetime", "index": { "KEY": { "summary": "...", "board": "...", "status": "..." } } }`. Clear the name index from in-context memory — all subsequent initiative lookups within this sub-agent read from the file on demand rather than scanning the full in-memory object.
> **Health field — confirmed field ID and value format (Run 15):** `customfield_12111` is correct and returns data when explicitly requested. Value format is emoji-prefixed: `"🟢 On Track"`, `"🟡 At Risk"`, `"🔴 Off Track"`. Signal matching must check for `"on track"` / `"at risk"` / `"off track"` (case-insensitive) — do NOT check for `"green"` / `"amber"` / `"red"`, those strings do not appear in the values. If health signals appear absent in a run, verify the `fields` parameter includes `customfield_12111` — ad-hoc extraction scripts in prior runs probed `customfield_14343`/`14344` which do not exist on these issues.

1b. **Resolve blockers** — for each initiative that has an `is blocked by` issue link, fetch the blocking issue with `fields=key,summary,status,project,customfield_12121,customfield_12122,customfield_14342,updated`. Determine `in_program_scope` by checking whether `customfield_14342` contains option ID `17894`. Calculate `days_blocked` from the link creation date. Set `stale = true` if `updated` is more than 7 days ago. Apply the elevated signal weight (4) for out-of-scope stale blockers.
1c. **Epic context check** — for any initiative whose release date (`customfield_12114`) has passed and which is still in a delivery status, fetch all child epics using JQL: `issueType = Epic AND parent = [initiative key]` with `fields=key,status`. Classify using the five classifications defined in the Epic Context Check table: `backlog_overdue`, `in_progress_overdue`, `not_closed_out`, `partial_delivery`, or `no_epic_data`. Apply the `release_date_overdue` signal only for `backlog_overdue` (weight 3) and `no_epic_data` (weight 1). Score 0 for all other classifications — route to DQ tracking instead. Epic fetches are per-initiative (Jira JQL does not support a single bulk parent-IN call for child epics). Fire these in parallel up to the Jira API rate limit — the overdue subset is typically small.
1d. **Stamp DQ labels** — for every initiative classified as `not_closed_out` in Step 1c, stamp the label `ro-not-closed-out` via `editJiraIssue` (add to labels array; do not overwrite other existing labels). In the same step, query Jira for any PLAYER initiative that currently carries this label but was NOT classified as `not_closed_out` this run — remove the label from those. This keeps the label set accurate mid-week even before the DQ workflow clears everything at end of its run.
2. **Build Slack channel discovery** — dynamically find all channels with `romania` or `ip` in their name (including private/temp) via Slack MCP. Runs in parallel with Steps 1 and 4+5.
3. **Build signal evaluator** — logic module that scores each topic across all three sources
4. **Build Slack scanner** — reads discovered channels, identifies high-discussion/risk threads; for Slack-only topics, attempts to match to a Jira initiative using the name index at `references/jira-name-index-temp.json` and includes the key if found. **Scan priority**: (1) read `references/slack-channels.md` and scan all known channels first using a **7-day** message window; (2) for channels returned by Step 2 that are NOT in the reference file, scan with a **24-hour** window only — new channels get a lighter first pass until confirmed high-signal. This prevents unknown channels from expanding the context footprint on first encounter.
4b. **Sync channel reference** — runs immediately after Step 4 completes, using the per-channel activity data captured during the scan. Three operations, all using targeted Edit calls on `references/slack-channels.md`:
  1. **Add new channels**: for any channel returned by Step 2 discovery that is not already in the reference file, append a new row with `last_active` set to today's date and a brief description inferred from the channel name.
  2. **Refresh active channels**: for any channel where at least one message was read during the Step 4 scan, update its `last_active` date to today.
  3. **Prune stale channels**: for any channel in the reference file where `last_active` is 30+ days before today AND no messages were found during the Step 4 scan, remove that row entirely. Do not prune channels whose `last_active` is unknown (`—`) — leave them for the next run to assess.
  Do not rewrite the whole file — only touch rows that changed. Log any pruned channels in the run notes.
5. **Build CPR scanner** — queries Notion for recent CPR meeting note pages, extracts unresolved/recurring agenda items. Runs in parallel with Steps 1 and 2.
6. **Merge and cross-reference** — main session reads `references/jira-signals-temp.json`, `references/slack-signals-temp.json`, and `references/notion-signals-temp.json`. Verify `run_number` in each file matches the current run before merging — abort if any file is missing or stale. Merge all signal arrays by initiative key (union sources, union signals, sum score_contribution). Flag cross-source discrepancies: Jira stale but Slack active → high priority; Slack risk signal but no Jira issue found → triage request.
6a. **Score and upsert risks** — for each detected topic: (1) skip if `suppressed = true`; (2) check `comments_posted` — if an entry exists with `run_number` equal to the current run, skip auto-comment for this issue (one-comment-per-run guard); (3) accumulate signal weights + cross-source bonus → raw score; (4) apply timeline proximity amplifier using `customfield_12114`; (5) derive severity; (6) infer category from signal pattern; (7) pull `product_lead` and `engineering_lead` from `customfield_12121`/`customfield_12122` on the linked initiative; (8) calculate `days_to_release`; (9) set `trend` by comparing to `score_last_run`; (10) set `new_this_run`; (11) upsert into JSON register.

**Scoring output format — compact table, no prose per risk.** Produce a single table covering all risks scored this run:

```
| ID     | score | final | sev | trend | signals_added         | notes_update                              |
|--------|-------|-------|-----|-------|-----------------------|-------------------------------------------|
| RR-011 | 6     | 9.0   | H   | ↑     | stale_7d, health_red  |                                           |
| RR-019 | 4     | 6.0   | H   | →     | slack_hr              | SSU "blocked by wallet" → likely PLT-330  |
| RR-041 | 3     | 4.5   | M   | 🆕    | cpr_recurring         |                                           |
```

- `score` = raw signal total; `final` = amplified score
- `signals_added` = only signal codes newly triggered this run (delta vs prior run — omit codes already present in prior `signals[]`)
- `notes_update` = one-line free-text for any inference that doesn't fit a signal code — this is what gets written to the `notes` field in the register. Leave blank if nothing to note.
- No per-risk narrative paragraphs. All reasoning must be captured in `signals_added` or `notes_update` — if it cannot fit there, it is not needed downstream.
6a-write. **Write state checkpoint** — immediately after the Step 6a scoring table is complete, produce `scores.json` and run `register_utils.py`. Do not wait until after Notion sync. This ensures scored state is preserved even if the session runs out of context before later steps complete.

**scores.json format:**
```json
{
  "run_number": 18,
  "run_date": "2026-05-28",
  "scored_risks": [
    {
      "id": "RR-001",
      "score": 6,
      "signals": ["stale_7d", "health_red"],
      "notes": "one-line from notes_update column — blank if empty",
      "planned_release_date": "2026-06-15",
      "days_to_release": 18
    }
  ],
  "new_risks": [
    {
      "id": "RR-052",
      "title": "Short topic description",
      "category": "technical",
      "workstream": "IP",
      "jira_issues": ["IP-45"],
      "score": 4,
      "signals": ["health_red"],
      "notes": "",
      "planned_release_date": null,
      "days_to_release": null
    }
  ],
  "resolved_ids": ["RR-008"],
  "suggested_dependencies": [
    {
      "initiative_a": "IP-45",
      "initiative_b": "IP-62",
      "suggested_link": "IP-45 is blocked by IP-62",
      "confidence_reason": "both named in same #ro-ip-temp thread (2026-05-28): 'wallet must be live before registration can complete'"
    }
  ]
}
```

Run:
```bash
python register_utils.py apply-scores --file scores.json
```

`apply-scores` handles: trend/severity computation, occurrences increment, `consecutive_misses` reset, new risk insertion, `resolved_ids` → status Resolved, suggested_dependency upsert, `run_number` bump, atomic write. **Idempotency guard**: if the register already has `run_number` matching `scores.json`, the command skips with a message — safe to re-run on session resume without double-incrementing occurrences.
6b. **Notion sync** — for any risk with severity = High OR occurrences >= 2, create or update the corresponding page in the "RO Migration Risk Register" Notion database (collection `7f410211-1a06-4fcc-b10c-ab58571a781a`).

**Before syncing**, run to get pre-computed property values for all pages:
```bash
python register_utils.py notion-sync-plan
```
This outputs a CREATE section (risks with `notion_page_id = null`) and an UPDATE section (existing pages). Use this output as the source of truth for the Notion API calls — do not re-derive property values from the register directly.

**Batch creates**: `notion-create-pages` accepts up to 100 pages per call — submit all new pages in a single batch rather than one-by-one. **Updates**: use `notion-update-page` with `command: "update_properties"` — `content_updates` is NOT a parameter for `update_properties` and should be omitted. After writing, read back the `Suppressed` checkbox for all synced pages.

**After all Notion operations complete**, produce `finalize.json` and run:
```bash
python register_utils.py finalize --file finalize.json
```

**finalize.json format:**
```json
{
  "run_number": 18,
  "notion_page_ids": {
    "RR-051": "abc123def456abc123def456abc12345",
    "RR-052": "789abc789abc789abc789abc78901234"
  },
  "suppressed_updates": {
    "RR-007": true
  },
  "comments_posted": [
    {
      "risk_id": "RR-001",
      "jira_key": "IP-45",
      "date": "2026-05-28",
      "comment_id": "12345678"
    }
  ],
  "sd_increments": ["SD-001"],
  "meta": {
    "last_run": "2026-05-28",
    "run_number": 18
  }
}
```

`finalize` writes: `notion_page_id` for all newly created pages, `suppressed` sync from Notion readback, `comments_posted` entries (audit trail, never overwritten), `times_suggested` increments for SDs, `last_run`/`run_number` header update. All via atomic write.
6c. **Mark resolved risks** — any risk in the JSON register that was NOT detected this run: increment `consecutive_misses`; at 1 miss set status = Resolved in Notion; at 2 misses set status = Closed and archive in JSON
6d. **Dependency inference** — identify all pairs of in-scope initiatives that co-occurred in the same Slack thread or CPR agenda item this run. For each pair: (1) confirm no existing Jira link via `issuelinks`; (2) pass to Claude with initiative summaries, categories, signal patterns, and the verbatim co-occurrence evidence — ask Claude to assess whether a dependency is plausible and in which direction, with explicit reasoning; (3) only proceed if Claude returns high confidence. Check the `suggested_dependencies` register — if this pair was previously dismissed, only re-surface if `times_suggested` has incremented 3+ times since dismissal. Upsert into `suggested_dependencies` in the JSON register.
7. **Digest formatter** — reads severity from register; prepends risk ID (e.g. `RR-001`) to each bullet; promotes Escalated risks to the 🚨 section; produces the Slack message with @mentions for Jon and Niels.
   > **Hyperlink rule (mandatory):** Every Jira key anywhere in the digest — headlines, bullets, table cells, description sentences — MUST be a markdown hyperlink: `[KEY](https://axilis.atlassian.net/browse/KEY)`. No exceptions for supporting-context references like `FPT-300` or `TRX-2542`. Bare keys are never acceptable. Run `validate_register.py --digest <file>` to catch violations before posting.
8. **Auto-commenter** — posts to stale/flagged Jira issues
9. **Schedule** — register as a Monday 09:00 GMT routine
10. **Validate register** — before committing, run the eval harness to catch silent failures:
    ```bash
    python "RO Migration to Betler/validate_register.py" --auto-prev --post-notion-sync
    ```
    The harness runs 4 eval suites:
    - **Structural** — valid JSON shape, score range (0–30), severity/score alignment, Escalated threshold (≥6), all Closed risks have score=0, `new_this_run` reset
    - **Regression** — occurrences never decrease, no risk deleted, run_number incremented by 1, no direct Closed→Escalated jump, reopened risks have consecutive_misses=0
    - **Trend** — stored `trend` symbol matches `score` vs `score_last_run` arithmetic (exceptions: `🆕` and zero→zero reopens)
    - **Notion sync** (`--post-notion-sync`) — every non-Closed/Resolved risk with severity=High or occurrences≥2 has a `notion_page_id` set
    If any eval fails, fix the register before committing. Exit code 0 = all passed, 1 = failures.

11. **Git commit and push** — after evals pass and digest is posted, run:
    ```bash
    git add "RO Migration to Betler/risk-register.json"
    # also stage if Step 4b made changes:
    git add "references/slack-channels.md"
    git commit -m "chore(risk-crawler): Run N (YYYY-MM-DD) — [N] risks, [N] escalations"
    git push origin main
    ```
    Stage only `risk-register.json` and `references/slack-channels.md`. Do not stage helper scripts, temp files, or `.pkl` artifacts. The exact command `git push origin main` is required — the auto-mode classifier blocks the push unless this specific command appears in the task definition.

12. **Clean up run-specific temp files** — delete these after each run:
    ```bash
    rm scores.json finalize.json
    rm references/jira-signals-temp.json references/slack-signals-temp.json references/notion-signals-temp.json
    rm references/jira-name-index-temp.json
    ```
    **Do NOT delete** `register_utils.py` or `jira_extract.py` — these are permanent utilities. If any `extract_*.py`, `update_register.py`, or `finalize_register.py` files exist from a pre-utility run, delete those too.

### Open decisions to confirm before build:
- [x] Niels De Winde's Slack handle — confirmed `U04MM3C1H8U`
- [x] Initiative count — confirmed 200 initiatives across 6 boards (IP, PLAYER, GAM, DAP, PLT, SOC); query must paginate
- [ ] Notion risk register parent page — confirmed: https://app.notion.com/p/superbet/e03b4e84b51e40089f6663e9f14576b3

---

## Staleness Thresholds (proposed — to be confirmed)
| Issue state | Stale after |
|---|---|
| In Progress | 7 days no update |
| To Do / Backlog (with external signal) | 14 days |
| Backlog (no external signal) | 30 days |

---

## Risk Register

Persisted between runs as `risk-register.json` in this directory. Each detected topic is stored as a risk entry and updated on every crawler run.

```json
{
  "last_run": "ISO date",
  "suggested_dependencies": [],
  "risks": [
    {
      "id": "RR-001",
      "title": "Short topic description",
      "category": "dependency",
      "sources": ["jira", "slack"],
      "signals": ["stale_7d", "high_discussion"],
      "score": 7,
      "score_last_run": 4,
      "trend": "worsening",
      "severity": "high",
      "impact": "high",
      "status": "monitoring",
      "workstream": "IP",
      "jira_issues": ["IP-45"],
      "product_lead": "Jane Smith",
      "engineering_lead": "John Doe",
      "planned_release_date": "2026-05-22",
      "days_to_release": 18,
      "notion_page_id": null,
      "first_seen": "ISO date",
      "last_seen": "ISO date",
      "occurrences": 2,
      "consecutive_misses": 0,
      "new_this_run": false,
      "suppressed": false,
      "suppressed_by": null,
      "mitigation_action": "",
      "mitigation_owner": "",
      "mitigation_target_date": null,
      "mitigation_status": "none",
      "epic_context": {
        "classification": "backlog_overdue",
        "active_epics": ["PLAYER-999", "PLAYER-1001"],
        "done_epics": 3,
        "wont_do_epics": 1
      },
      "comments_posted": [
        {
          "jira_key": "IP-45",
          "date": "2026-05-11",
          "run_number": 6
        }
      ],
      "slack_threads": [
        {
          "url": "https://superbet.slack.com/archives/C.../p...",
          "channel": "#ip-romania-discussions",
          "summary": "KYC API missing from Betler wallet"
        }
      ],
      "blockers": [
        {
          "key": "TRANSACT-123",
          "summary": "Payment platform upgrade",
          "status": "In Progress",
          "project": "TRANSACT",
          "in_program_scope": false,
          "product_lead": null,
          "engineering_lead": "Alex Jones",
          "days_blocked": 21,
          "stale": true
        }
      ]
    }
  ]
}
```

**Fields:**
| Field | Description |
|---|---|
| `id` | Auto-incremented identifier (RR-001, RR-002, …) |
| `category` | Risk category — see Risk Categories |
| `sources` | Which sources detected this risk (jira / slack / cpr) |
| `signals` | Raw signal codes that triggered detection |
| `score` | Raw cumulative signal score this run (before timeline amplification) |
| `score_last_run` | Score from the previous run — used to calculate trend |
| `trend` | `improving` / `stable` / `worsening` — derived by comparing `score` to `score_last_run` |
| `severity` | Auto-calculated from amplified score — see Scoring Logic |
| `impact` | Auto-calculated — see Scoring Logic |
| `status` | Lifecycle state — see Risk Lifecycle |
| `workstream` | Jira board of the primary linked initiative (IP / GAM / DAP) |
| `jira_issues` | Array containing **exactly one** Jira initiative key. Each risk entry covers a single initiative. Child epics linked to that initiative are recorded in `epic_context`, not here. Never group peer initiatives under a single risk entry — create a separate entry for each. |
| `product_lead` | Product Lead display name from `customfield_12121` on the linked initiative |
| `engineering_lead` | Engineering Lead display name from `customfield_12122` on the linked initiative |
| `planned_release_date` | ISO date — the Planned Release Date (`customfield_12114`) as of the current run. Stored each run after scoring so the next run can detect slips by comparing against this value. |
| `days_to_release` | Days until Planned Release Date (`customfield_12114`) of the primary initiative; null if not set |
| `notion_page_id` | Set once synced to Notion; used to update rather than duplicate |
| `first_seen` | ISO date of first detection |
| `last_seen` | ISO date of most recent detection |
| `occurrences` | Number of crawler runs this risk has been detected |
| `consecutive_misses` | Runs since the risk was last detected (used for auto-resolution) |
| `new_this_run` | True if this is the first run the risk has appeared |
| `suppressed` | If true, risk is excluded from scoring and digest |
| `suppressed_by` | Name of person who suppressed (Jon, Niels, or initiative Product/Engineering Lead) |
| `mitigation_action` | Free text description of the mitigation being taken |
| `mitigation_owner` | Person accountable for the mitigation |
| `mitigation_target_date` | ISO date by which mitigation should be complete |
| `mitigation_status` | `none` / `planned` / `in_progress` / `complete` |
| `epic_context` | Object populated when release date is overdue: `classification` (`backlog_overdue` / `in_progress_overdue` / `not_closed_out` / `partial_delivery` / `no_epic_data`), `active_epics` (keys of epics still in progress), `done_epics` (count), `wont_do_epics` (count) |
| `comments_posted` | Array of Jira comment records: `{jira_key, date, run_number}`. One entry per comment posted, appended each run. Never overwritten — provides a full audit trail. Used to render the `💬` indicator in the digest and to enforce the one-comment-per-run guard. |
| `slack_threads` | Array of Slack thread evidence objects: `{url, channel, summary}`. `url` is the full permalink (e.g. `https://superbet.slack.com/archives/C.../p...`). Populated whenever a Slack thread is the source of a signal. Used to hyperlink evidence in the digest. |
| `blockers` | Array of blocker objects (populated for Dependency category risks only — see Dependency Handling) |

---

## Dependency Handling

When an in-scope initiative has an `is blocked by` Jira link, the crawler fetches the blocking issue and enriches the risk entry with full context. This applies regardless of whether the blocker is inside or outside the Romania migration program.

### What is fetched per blocker
| Field | Source |
|---|---|
| `key` | Blocker issue key |
| `summary` | Blocker issue title |
| `status` | Current Jira status of the blocker |
| `project` | Project board the blocker belongs to |
| `in_program_scope` | Whether the blocker has program tag `17894` (🇷🇴 Romania migration) |
| `product_lead` | `customfield_12121` on the blocker, if set |
| `engineering_lead` | `customfield_12122` on the blocker, if set |
| `days_blocked` | Days since the `is blocked by` link was created |
| `stale` | True if the blocker has had no update in 7+ days |

### In-scope vs out-of-scope blockers

| Blocker type | Treatment |
|---|---|
| **In-scope** (`in_program_scope = true`) | Owned within the program — surfaced as a dependency risk, programme lead can action directly |
| **Out-of-scope** (`in_program_scope = false`) | Owned by another team — surfaced with a distinct ⛔ marker in the digest, indicating cross-team escalation is required |

### Blocker signal weight adjustment

If a blocker is out-of-scope AND stale, the dependency signal weight increases from 2 to **4** — an external team owning a stale blocker on an in-scope initiative is treated as a high-priority risk regardless of other signals.

### In the digest

Dependency risks display a blocker sub-line beneath the main risk bullet:
```
• [RR-007] ↑ *IP-45: Reality check* — Dependency | PL: Jane Smith, EL: John Doe
  ⛔ Blocked by: TRANSACT-123 (Payment platform upgrade) — out-of-program | EL: Alex Jones | stale 21d
  📅 12 days to release · Week 3
```

If an initiative has multiple blockers, each is listed on its own sub-line. Out-of-scope blockers always appear before in-scope blockers.

### In the digest — dedicated section for out-of-scope blockers

All out-of-scope blockers are additionally aggregated into a standalone section at the end of the digest, giving the programme lead a single view of everything requiring cross-team action:
```
⛔ *Cross-team dependencies requiring action*
• IP-45 blocked by TRANSACT-123 (Alex Jones) — stale 21d · 📅 12 days to release
• IP-62 blocked by WALLET-88 (no EL set) — stale 9d
```

---

## DQ Integration — Player Data Quality Workflow

When the Epic Context Check classifies an initiative as `not_closed_out`, the crawler stamps the Jira label `ro-not-closed-out` on that initiative. This signals to the Player Jira Data Quality workflow (which runs the same week) that the initiative needs closing out.

The DQ workflow reads this label, appends a note to the relevant squad's Slack message, then removes all `ro-not-closed-out` labels from PLAYER initiatives at end of its run. This ensures labels are always fresh: re-stamped by the crawler each Monday, cleared by the DQ workflow the same week.

---

## Risk Categories

Every risk is assigned a category at detection time. The crawler infers the most likely category from signal patterns; it can be corrected manually in the Notion register.

| Category | Description | Typical signals |
|---|---|---|
| **Technical** | Implementation blocker, integration failure, platform instability | Jira blocked/flagged, Slack technical discussion, Health Status Red |
| **Dependency** | Blocked on another team, initiative, or initiative link | Jira `is blocked by` link, stale initiative with active upstream discussion |
| **Resource** | Capacity gap, staffing issue, skills shortage | Slack discussion about team bandwidth, stale initiative with no Engineering Lead set |
| **Scope** | Requirements unclear or changing, initiative not well-defined | Missing PRD/description, CPR recurring without resolution, Slack scoping discussions |
| **Compliance** | Regulatory, legal, or data privacy constraint | Compliance-related initiative keywords, CPR items without decision |
| **Timeline** | Delivery date at risk, schedule slippage | Planned Release Date proximity + Health Status Amber/Red, stale in-delivery initiative |

---

## Scoring Logic

### Step 1 — Raw signal score

Each detected signal carries a weight (defined in the Signal Logic tables above). Scores accumulate across all sources for a given risk in a single run. A cross-source bonus of **+2** applies whenever signals from 2 or more sources contribute to the same risk.

### Step 2 — Timeline proximity amplifier

If the linked initiative has a Planned Release Date (`customfield_12114`) set, the raw score is multiplied by:

| Days to Planned Release Date | Multiplier |
|---|---|
| ≤ 14 days | ×2.0 |
| 15–30 days | ×1.5 |
| 31–60 days | ×1.25 |
| > 60 days or no date set | ×1.0 |

### Step 3 — Severity threshold

| Amplified score | Severity |
|---|---|
| 1–2 | **Low** — on radar, no immediate action |
| 3–5 | **Medium** — warrants monitoring |
| 6+ | **High** — requires active attention |

Severity is re-calculated fresh each run from live signals. Historical recurrence is tracked separately via `occurrences` and drives the Escalated lifecycle state independently. The raw (pre-amplification) score is stored in `score` for trend comparison across runs.

### Impact (auto-calculated)
| Condition | Impact |
|---|---|
| Linked Jira issue priority = Critical or High | **High** |
| Linked Jira issue priority = Medium, or 10+ Slack replies | **Medium** |
| Linked Jira issue priority = Low, or no Jira issue found | **Low** (default) |

---

## Notion Sync

A dedicated Notion database **"RO Migration Risk Register"** is created in the same Notion space as the CPR databases.

**Sync criteria:** only risks with `severity = high` OR `occurrences >= 2` are synced. Low-confidence, first-seen Medium/Low risks remain JSON-only until they recur.

**Suppression sync:** the `Suppressed` checkbox is read at Step 1a (register load), not after sync — see Step 1a above. After writing risk property updates in Step 6b, write back any `suppressed` state changes discovered during the run (i.e. a risk un-suppressed mid-run). The "Suppressed By" text field is updated alongside. This allows programme leads to suppress or un-suppress risks directly from Notion without touching the JSON.

**Database schema:**
| Field | Type |
|---|---|
| Risk ID | Title |
| Description | Text |
| Category | Select: Technical / Dependency / Resource / Scope / Compliance / Timeline |
| Severity | Select: High / Medium / Low |
| Impact | Select: High / Medium / Low |
| Trend | Select: Worsening ↑ / Stable → / Improving ↓ |
| Status | Select: Open / Monitoring / Escalated / Resolved / Closed / Suppressed |
| Workstream | Select: IP / GAM / DAP |
| Sources | Multi-select: Jira / Slack / CPR |
| Linked Jira Issues | Text (comma-separated keys) |
| Product Lead | Text |
| Engineering Lead | Text |
| Days to Release | Number |
| First Seen | Date |
| Last Seen | Date |
| Occurrences | Number |
| Mitigation Action | Text |
| Mitigation Owner | Text |
| Mitigation Target Date | Date |
| Mitigation Status | Select: None / Planned / In Progress / Complete |
| Suppressed | Checkbox — when checked: excludes the risk from the Slack digest entirely and blocks all Jira auto-comments for this risk. The crawler reads this field on each run and syncs it back to `suppressed = true` in the JSON register. |
| Suppressed By | Text |
| Blockers | Text (one line per blocker: key · summary · owner · days blocked) |
| Out-of-Program Blocker | Checkbox — true if any blocker is outside the Romania migration program |
| Max Days Blocked | Number — longest active blocker duration in days |

On first sync the returned Notion page ID is stored in `notion_page_id` in the JSON so subsequent runs update the existing page rather than creating a duplicate. Suppressed risks are synced with Status = Suppressed and excluded from all digest outputs.

---

## Risk Lifecycle

| Status | Trigger | Action |
|---|---|---|
| **Open** | First detected this run | Add to JSON register; set `new_this_run = true`; `trend = stable` (no prior score to compare) |
| **Monitoring** | Detected in a subsequent run | Increment `occurrences`; calculate trend vs `score_last_run`; sync to Notion if severity = High or `occurrences >= 2` |
| **Escalated** | `occurrences >= 3` OR cross-source High for 2+ consecutive runs | Set status = Escalated; update Notion; promote to 🚨 section in digest |
| **Resolved** | Not detected for 1 run | `consecutive_misses = 1`; update Notion status to Resolved; include in digest as resolved this week |
| **Closed** | Not detected for 2 consecutive runs | `consecutive_misses = 2`; update Notion status to Closed; remove from active digest |
| **Suppressed** | Manually set by Jon, Niels, or initiative Product/Engineering Lead | Set `suppressed = true`, record `suppressed_by`; exclude from all scoring and digest outputs; sync suppressed status to Notion |

### Mitigation tracking

When a mitigation is underway, `mitigation_status` progresses through: `none → planned → in_progress → complete`. Setting `mitigation_status = complete` does not automatically close a risk — the crawler still checks for live signals. The risk closes naturally once signals are no longer detected for 2 consecutive runs.

---

## Next Steps
1. Confirm Niels De Winde's Slack user ID (needed for @mention in digest)
2. Build and test signal logic against a known at-risk issue
3. Schedule routine
4. Update PLYRTPM-33 with this plan as description

---

## Sub-Agent Prompt Templates

These prompts are passed verbatim to `Agent(prompt=...)` at run time. Substitute `{run_number}`, `{last_run_date}`, and `{register_path}` before dispatch. Each prompt instructs the sub-agent to read this skill file for full signal logic detail and return a one-line summary only — data travels via temp files, not via the return value.

---

### JIRA_COLLECTOR_PROMPT

```
You are the Jira collector sub-agent for the Romania Risk Crawler (PLYRTPM-33), Run {run_number}.

## Project directory
C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler

## First: read these files for full signal definitions and field IDs
- romania-risk-crawler.md (Steps 1, 1b, 1c, 1d, 1e — Signal Logic section, Epic Context Check)
- references/notion-risk-register-schema.md (not needed for Jira but load anyway for run context)
- risk-register.json (read current state for slip detection; path: {register_path})

## Tools to load (ToolSearch)
select:mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__searchJiraIssuesUsingJql,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__getJiraIssue,mcp__b846195e-69b9-4ade-88d4-18e6a3f23890__editJiraIssue

## Run inputs
- run_number: {run_number}
- last_run_date: {last_run_date}

## Your tasks (in order)
1. Execute Step 1 from the skill: fetch all in-scope initiatives using the confirmed JQL. Request only the specified fields. Paginate until isLast=true.
2. Execute Step 1b: build the name index and write it to references/jira-name-index-temp.json. Discard raw API response from context immediately after.
3. Execute Step 1c: evaluate signals for every initiative, including Epic Context Check for overdue initiatives.
4. Execute Step 1d: stamp ro-not-closed-out labels on PLAYER initiatives as needed.
5. Execute Step 1e (blocker resolution): fetch blocking issues for any initiative with an "is blocked by" link.

## Output
Write to: references/jira-signals-temp.json
Use the Sub-agent output file format defined in the skill (run_number, generated, signals array).

## Context rules
- Discard raw API payloads immediately after field extraction
- For responses > 50k chars: use PowerShell ConvertFrom-Json to reduce before processing
- Return ONE LINE only: "Jira collector complete: N initiatives scanned, N signals written to jira-signals-temp.json"
- The full signal list travels via the output file, not your response
```

---

### NOTION_COLLECTOR_PROMPT

```
You are the Notion CPR collector sub-agent for the Romania Risk Crawler (PLYRTPM-33), Run {run_number}.

## Project directory
C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler

## First: read these files
- romania-risk-crawler.md (Step 5 — CPR scanner, Notion CPR Database Inventory, Signal Logic section 3)
- risk-register.json (read current state; path: {register_path})

## Tools to load (ToolSearch)
select:mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-query-data-sources,mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-search,mcp__3da07a3d-3738-4c02-999f-340a5e731aae__notion-fetch

## Run inputs
- run_number: {run_number}
- last_run_date: {last_run_date}

## Your tasks
Execute Step 5 from the skill: query all CPR databases listed in the Notion CPR Database Inventory. Extract unresolved and recurring agenda items. Apply the Notion signal weights (CPR Signal Logic table). Structured DB signals carry full weight; unstructured page signals carry reduced weight — flag them as low-confidence.

## Output
Write to: references/notion-signals-temp.json
Format:
{
  "run_number": {run_number},
  "generated": "<ISO datetime>",
  "signals": [
    {
      "key": "IP-45",
      "sources": ["cpr"],
      "signals": ["cpr_recurring"],
      "score_contribution": 3,
      "days_to_release": null,
      "planned_release_date": null,
      "product_lead": null,
      "engineering_lead": null,
      "epic_context": null,
      "slack_threads": [],
      "label_actions": [],
      "notes": "brief evidence note"
    }
  ]
}

## Context rules
- Discard raw Notion page content after extracting signals — retain only the signal objects
- Return ONE LINE only: "Notion collector complete: N CPR databases scanned, N signals written to notion-signals-temp.json"
```

---

### SLACK_COLLECTOR_PROMPT

```
You are the Slack collector sub-agent for the Romania Risk Crawler (PLYRTPM-33), Run {run_number}.

## Project directory
C:\Users\JonVince\Documents\GitHub\International-Programs\RO Migration to Betler

## First: read these files
- romania-risk-crawler.md (Steps 2, 4, 4b — Slack scanner, channel discovery, channel reference sync)
- references/slack-channels.md (known channel IDs and last_active dates)
- references/jira-name-index-temp.json (written by Jira collector — verify run_number={run_number} before using)
- risk-register.json (path: {register_path})

## Tools to load (ToolSearch)
select:mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_search_public_and_private,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_search_channels,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_read_channel,mcp__95268b0a-2ab0-44e0-9a74-e956c9f0dc3b__slack_read_thread

## Run inputs
- run_number: {run_number}
- last_run_date: {last_run_date}

## Your tasks (in order)
1. Execute Step 2: discover all Slack channels with "romania" or "ip" in their name.
2. Execute Step 4: scan channels using the priority and window rules from the skill (7-day for known channels, 24-hour for new channels). For each signal, attempt to match the topic to a Jira initiative key using the name index.
3. Execute Step 4b: sync references/slack-channels.md — add new channels, refresh last_active for active channels, prune channels stale for 30+ days. Use targeted Edit calls (one per changed row), never a full file rewrite. Do NOT prune channels with unknown last_active.

## Output
Write to: references/slack-signals-temp.json
Use the same format as the Jira collector output (run_number, generated, signals array with sources=["slack"]).
Include slack_threads array for each signal: [{url, channel, summary}].

## Context rules
- Discard raw Slack message content after extracting signal objects — never hold full channel histories in context
- Return ONE LINE only: "Slack collector complete: N channels scanned, N signals written to slack-signals-temp.json, N channel rows updated in slack-channels.md"
```
