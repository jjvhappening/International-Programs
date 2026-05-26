---
name: IP Programme Artefacts Reference
description: Definitive list of artefacts used across International Programs lifecycle — with stage matrix, example links, and specific improvement actions
type: reference
project: International Programs
---

# IP Programme Artefacts

Last updated: 2026-05-22

Artefacts are specific documents requiring input/output throughout a programme's lifecycle. Covers all three IP programme types: market entries, platform migrations, and cross-area product programmes.

**Design steer:** Move away from manual updates toward a data-driven, Jira-first approach — minimal IPM admin overhead, maximum recency and context.

Evidence: Slack (#ip-manage, #ip-romania-discussions, #ip-croatia-retail-discussions), Notion workspace discovery, IP Context File. Council review: 2026-05-22.

---

## Stage Matrix

`●` = primary (artefact is actively created or updated in this stage)
`○` = supporting (artefact is referenced or lightly maintained)

| # | Artefact | Scoping | Delivery | Go-Live | Hypercare | Aftercare |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Scoping Document | ● | ○ | | | |
| 2 | IP Scoping Process | ● | | | | |
| 3 | AML Risk Derivation Matrix | ● | ○ | | | |
| 4 | Feature Readiness Overview | ○ | ● | ○ | | |
| 5 | Stakeholder Map / RACI | ● | ○ | | | |
| 6 | Q&A / Open Questions Register | ● | ● | ○ | | |
| 7 | Communications Plan | ● | ● | ○ | | |
| 8 | Programme Calendar | ○ | ● | ○ | | |
| 9 | Decision Log | | ● | ○ | | |
| 10 | Budget / Cost Tracker | ● | ● | | | ○ |
| 11 | Risk Register / RAID Log | ○ | ● | ○ | ● | |
| 12 | Cross-Programme Dependency Register | | ● | ○ | | |
| 13 | All Areas Update | | ● | ○ | | |
| 14 | SteerCo Deck | | ● | | ○ | |
| 15 | Pulse Check | | ● | | ● | |
| 16 | Go-Live Checklist | | ○ | ● | | |
| 17 | Regression Test Results | | ○ | ● | | |
| 18 | Go/No-Go Decision Record | | | ● | | |
| 19 | Hypercare Report | | | | ● | |
| 20 | Issue Log | | | | ● | |
| 21 | Retrospective / Lessons Learned | | | | | ● |
| 22 | Programme Closure Report | | | | | ● |

---

## Priority improvements (TPM-owned quick wins)

No stakeholder complexity — pure duplication of existing Jira data:

1. **Feature Readiness Overview → Jira dashboard** — highest ROI; data already in Jira
2. **Issue Log → Jira JQL saved filter** — eliminates double-entry; Chase/Jira link is the only change
3. **Risk Register → standardise on Jira** — RO Migration pattern already proven; extend to all programmes
4. **Go-Live Checklist → Jira sub-tasks on a Go-Live Gate epic** — live readiness % replaces "read the page"
5. **All Areas Update → auto-generated from JQL** — IPM reviews rather than writes

Decision Log is high value but requires **automated capture** (Slack → Jira), not just a new storage location.

---

## Implementation ownership

| Improvement | Who can implement |
|---|---|
| Feature Readiness → Jira dashboard | TPM-owned |
| Issue Log → Jira JQL | TPM-owned |
| Risk Register → Jira | TPM-owned |
| Go-Live Checklist → Jira sub-tasks | TPM-owned |
| Programme Calendar → Jira timeline | TPM-owned |
| Q&A Register → Jira label + saved filter | TPM-owned |
| Decision Log → Jira label + saved filter | TPM-owned for creation; **Slack/Claude integration** for capture |
| All Areas Update → auto-generated | Requires tooling build (Claude + JQL template) |
| Hypercare Report → auto-generated | Requires tooling build (Jira + Chase + Grafana) |
| Go/No-Go → Jira blocking link | TPM-owned (soft gate); workflow automation requires Jira admin |
| AML Risk Matrix → structured DB | Requires Compliance buy-in |
| Retro → structured follow-up cadence | TPM-owned process change |

---

## Artefacts

---

### Scoping

---

#### 1. Scoping Document

| | |
|---|---|
| **Stage** | Scoping (primary), Delivery (reference) |
| **Purpose** | Defines scope, objectives, and success criteria; requires formal sign-off before delivery begins |
| **Owner** | IPM / IP Lead |
| **Format** | Notion |
| **Example** | [Croatia Online Effort Assessment](https://www.notion.so/350032f852c580a7a963d5fb155f509c) — current scoping format in use |

**Assessment:** The scoping doc is a static Notion page that becomes a historical artefact the moment delivery begins — nobody updates it when scope changes.

**What to change:**
- Create a **"Programme" epic** in the relevant Jira project (e.g., DPW for RO, a new IP project for Croatia) with these fields populated at scoping: `Summary` = programme name, `Description` = scope statement, custom fields: `Success Criteria` (text), `Sign-off Status` (select: Draft / Under Review / Signed Off), `Go-Live Target Date` (date), `IP Lead` (user)
- The Notion scoping page remains as human-readable context, but links to the Jira epic as the live source of scope
- **Sign-off:** when stakeholders approve, the IPM transitions the epic status from "Scoping" → "Delivery" — this is the formal sign-off record, timestamped in Jira history, not a comment on a Notion page
- Add a Jira comment with approver names when transitioning

---

#### 2. IP Scoping Process

| | |
|---|---|
| **Stage** | Scoping (governance reference) |
| **Purpose** | Standard process guide governing how scoping is conducted across all programmes |
| **Owner** | IP Director |
| **Format** | Notion |
| **Example** | [IP Ways of Working — Problems & Proposed Solutions](https://www.notion.so/360032f852c581538580cb9423fc02bf) — closest current equivalent |

**Assessment:** This is a governance template, not a per-programme execution artefact. It gets read once at the start of scoping and then ignored.

**What to change:**
- Reclassify as a **Jira project template**: a saved configuration that, when applied to a new programme project, auto-creates: one Programme epic, one Go-Live Gate epic, standard labels (`ip-risk`, `ip-decision`, `ip-question`, `ip-blocker`), a default dashboard with the standard gadgets (see artefacts 4, 9, 11, 13)
- The Notion page becomes a brief "how to use the template" guide — not the template itself
- Review cadence: IP Director reviews the template every 6 months; version in Notion reflects current standard

---

#### 3. AML Risk Derivation Matrix

| | |
|---|---|
| **Stage** | Scoping (primary), Delivery (reference) |
| **Purpose** | Compliance and regulatory risk assessment for market entry programmes |
| **Owner** | IPM + Compliance |
| **Format** | Notion / Spreadsheet |
| **Example** | [AML Risk Derivation Matrix — Business Sign-off](https://www.notion.so/349032f852c581e09ccfff25491953a3) — live example from RO Migration |

**Assessment:** Currently a free-form document copy-pasted between programmes with inconsistent structure. Compliance team co-owns this and is conservative about tool changes that affect audit trails — any format change requires their buy-in.

**What to change (with compliance agreement):**
- Convert to a **Notion database** with one row per risk item and these properties: `Risk Area` (select: AML / KYC / Sanctions / PEP / Data / Licensing), `Regulation / Requirement` (text), `Current State` (text), `Target State` (text), `Gap` (text), `Risk Level` (select: Low / Medium / High / Critical), `Mitigation` (text), `Owner` (person), `Status` (select: Open / In Progress / Mitigated / Accepted / Closed), `Sign-off Date` (date)
- This makes risk status queryable and comparable across market entry programmes without changing the compliance team's workflow — they still fill in the same fields, just in a structured DB rather than a free-form page
- Filter view: `Status != Closed AND Risk Level in (High, Critical)` for SteerCo reporting

---

#### 4. Feature Readiness Overview

| | |
|---|---|
| **Stage** | Scoping (reference), Delivery (primary), Go-Live (gate) |
| **Purpose** | Per-squad assessment of feature readiness; gates go-live decision |
| **Owner** | IPM |
| **Format** | Notion |
| **Example** | [Feature Readiness on STAGE](https://www.notion.so/342032f852c580e2a014d6c012457b95) — current manual format showing IP RAG status per feature |

**Assessment:** This is a manual re-entry of data that already exists in Jira. Squads track feature completion in Jira — the IPM then reads Jira and writes a summary in Notion. Eliminating this is the highest-ROI quick win.

**What to change:**
- Create a **Jira dashboard** named `Feature Readiness — [Programme Name]`
- **Gadget 1 — Two-Dimensional Filter Statistics:** filter = `project = [PROGRAMME] AND issuetype = Epic AND "Programme" = "[Programme Name]"`, X-axis = `Component` (each component = one squad/area), Y-axis = `Status`. Shows completion by squad in a grid.
- **Gadget 2 — Filter Results (outstanding items):** filter = `project = [PROGRAMME] AND issuetype = Epic AND status not in (Done, Closed) AND component is not EMPTY ORDER BY component ASC`. Shows the open list.
- **Gadget 3 — Pie chart:** breakdown of epic statuses for the programme. Shows overall % complete at a glance.
- For RO Migration: filter on `project = DPW AND parent = PT-25` (the existing initiative structure)
- Share the dashboard URL with the team — this replaces the Notion page entirely. The Notion page can be archived.

---

#### 5. Stakeholder Map / RACI

| | |
|---|---|
| **Stage** | Scoping (primary), Delivery (reference) |
| **Purpose** | Maps ownership, approvals, and information flow across workstreams |
| **Owner** | IPM |
| **Format** | Notion / Lucidchart |
| **Example** | No dedicated example found — currently embedded in programme overview pages |

**Assessment:** Silently goes stale when people change roles or squads are restructured. The Lucidchart format in particular is hard to maintain.

**What to change:**
- Replace Lucidchart with a **Notion database** with these properties: `Name` (title), `Role / Squad` (text), `RACI` (select: Responsible / Accountable / Consulted / Informed), `Workstream` (multi-select: e.g., Platform / KYC / Payments / Compliance / Ops / Commercial), `Jira Username` (text — links to Jira user), `Slack Handle` (text), `Notes` (text)
- Group view by Workstream; filter view by RACI type
- Review trigger: add a recurring Jira task (`ip-admin` label, monthly) to validate RACI — takes 10 minutes vs the current "nobody does it" default

---

#### 6. Q&A / Open Questions Register

| | |
|---|---|
| **Stage** | Scoping (primary), Delivery (primary), Go-Live (reference) |
| **Purpose** | Captures open questions and answers from squads, legal, compliance |
| **Owner** | IPM |
| **Format** | Notion |
| **Example** | [Comtrade Engagement — Romania Migration](https://www.notion.so/356032f852c58172b403e230238c927b) — uses a similar open Q&A log structure |

**Assessment:** Questions get answered in Slack or Jira comments, but the register page is never updated. Becomes a stale list of already-answered questions that nobody trusts.

**What to change:**
- In the programme's Jira project, add label `ip-question` to any Task created for an open question
- **JQL saved filter:** `project = [PROGRAMME] AND labels = "ip-question" AND status != Done ORDER BY created DESC` — name it `Open Questions — [Programme Name]` and share it
- Fields on each question issue: Summary = the question, Description = context + where it came from, Assignee = who must answer, Due date = answer-by, Comment = the answer when resolved
- Resolution: add the answer as a comment, then close the issue — the closed issues form the answered-questions archive automatically
- Add this filter as a **Jira dashboard gadget** on the programme dashboard

---

#### 7. Communications Plan

| | |
|---|---|
| **Stage** | Scoping (primary), Delivery (primary), Go-Live (reference) |
| **Purpose** | Internal (squads, leadership) and external (regulatory, commercial partners) comms timelines and ownership |
| **Owner** | IPM / IP Lead |
| **Format** | Notion |
| **Example** | No dedicated IP example found — currently absent from tooling |

**Assessment:** Critical for market entries where regulatory and commercial comms have hard, non-negotiable deadlines (e.g., licence notification windows, press embargoes). Currently untracked.

**What to change:**
- Create a **Notion database** per programme with these properties: `Audience` (select: Squad / Leadership / Regulatory / Commercial Partner / Press / Internal All), `Message / Milestone` (title), `Channel` (select: Slack / Email / Meeting / Press Release / Regulatory Filing), `Owner` (person), `Planned Date` (date), `Status` (select: Not Started / Drafted / Sent / Confirmed), `Notes` (text)
- Filter view: `Status != Sent AND Planned Date <= today + 14 days` — shows upcoming comms obligations within a fortnight
- For regulatory comms with hard deadlines: link to the corresponding Jira task so slippage is visible on the programme dashboard

---

### Delivery

---

#### 8. Programme Calendar

| | |
|---|---|
| **Stage** | Delivery (primary), Go-Live (reference) |
| **Purpose** | Timeline of key milestones, ceremonies, and deadlines |
| **Owner** | IPM |
| **Format** | Notion / Google Cal |
| **Example** | [RO Migration Scheduling — meeting notes](https://docs.google.com/document/d/1YpF6VWpqL5EYltzCvnOEkxo67A0Nl9hq0b6n6sl9KYI) — milestone scheduling discussions (Google Docs) |

**Assessment:** A third source of truth for dates alongside Jira (due dates on epics) and Google Calendar (ceremonies). When a milestone slips in Jira, the Notion calendar is never updated.

**What to change:**
- Set **due dates on all programme epics** in Jira — this becomes the milestone calendar
- Use **Jira's Timeline view** (Roadmap): filter to the programme's parent epic (`parent = [PROGRAMME-EPIC]`), enable timeline view. This shows all epics as a Gantt-style view with due dates.
- For ceremonies: keep Google Calendar as-is — this is appropriate for recurring meetings
- The Notion calendar page is deleted; stakeholders are pointed to the Jira timeline URL
- When a date slips, it's updated in one place (Jira) and reflected everywhere

---

#### 9. Decision Log

| | |
|---|---|
| **Stage** | Delivery (primary), Go-Live (reference) |
| **Purpose** | Records material decisions, context, and approvals |
| **Owner** | IPM |
| **Format** | Notion |
| **Example** | No dedicated Notion page found — decisions currently posted as Slack messages in #ip-manage |

**Assessment:** The most consistently neglected artefact — structurally, because decisions happen in Slack and meetings, not in tools. Self-logging in Jira will fail the same way self-logging in Notion has always failed. The fix is automated capture, not a new location.

**What to change (two-phase):**
- **Phase 1 (now, TPM-owned):** Add label `ip-decision` to Jira tasks. JQL saved filter: `project = [PROGRAMME] AND labels = "ip-decision" ORDER BY created DESC` — name it `Decision Log — [Programme]`. When making a decision in Slack, paste the Jira issue link. Friction is low; completeness depends on discipline.
- **Phase 2 (automation):** Build a Slack workflow (or Claude integration) in #ip-manage that detects messages containing agreed phrases ("DECISION:", "we've decided", "confirmed:") and prompts with a one-click "Log to Jira" button. The button pre-populates a Jira task with the Slack message text, labels it `ip-decision`, and links it to the current sprint or programme epic. This removes the context-switch entirely.
- **Dashboard gadget:** add the `ip-decision` JQL filter as a "Filter Results" gadget on the programme dashboard — shows last 10 decisions at a glance

---

#### 10. Budget / Cost Tracker

| | |
|---|---|
| **Stage** | Scoping (establish baseline), Delivery (track actuals), Aftercare (final reconciliation) |
| **Purpose** | Tracks programme spend against budget — vendor contracts, infrastructure, headcount, licensing |
| **Owner** | IPM / Finance |
| **Format** | Spreadsheet / TBC |
| **Example** | [P&T Strategic Planning & Budgeting Cycle 2026](https://docs.google.com/spreadsheets/d/1D2yXaVAdjNZV6RQgvpvuUrI5SpjopTc6) — org-level budget context (Google Sheets) |

**Assessment:** Always exists somewhere as a spreadsheet nobody updates. Material for market entries and platform migrations where vendor costs are significant. No standard format or owner currently defined.

**What to change:**
- Define a **standard budget tracker template** in Google Sheets (not Notion — Finance tools live in Sheets): tabs for Budget (planned), Actuals (committed spend), Forecast (revised estimate), Variance
- Rows per cost category: Platform Vendor / Infrastructure / Headcount (contractor) / Licensing / Legal / Compliance / Other
- Link the Google Sheet to the programme's Notion page and Jira programme epic as a remote link
- Update cadence: monthly by IPM; Finance reviews quarterly
- Jira Jira custom field `Budget Status` (select: On Track / At Risk / Over) on the programme epic — IPM updates this monthly; it surfaces on the programme dashboard without needing to open the sheet

---

#### 11. Risk Register / RAID Log

| | |
|---|---|
| **Stage** | Delivery (primary), Hypercare (primary) |
| **Purpose** | Tracks Risks, Assumptions, Issues, Dependencies |
| **Owner** | IPM |
| **Format** | Notion / Jira |
| **Example** | [RO Migration Risk Register](https://www.notion.so/9dab74b2885b4f8f93aa73dad97ea6da) — current Notion-based register; also driven by automated [risk crawler in #ro-migration-risks](https://superbet.slack.com/archives/C0B0MB0Q4KD) |

**Assessment:** Already Jira-native for RO Migration via the risk crawler, which posts weekly digests to Slack. Other programmes use manual Notion tables. The crawler pattern is the standard to extend.

**What to change:**
- In each programme's Jira project, add label `ip-risk` to risk items. Fields: `Risk Category` (select: Technical / Compliance / Commercial / Operational / Dependency), `Probability` (select: Low / Medium / High), `Impact` (select: Low / Medium / High), `Mitigation` (text), `Risk Owner` (assignee), `Status` (select: Open / Mitigating / Closed / Accepted)
- **JQL saved filter:** `project = [PROGRAMME] AND labels = "ip-risk" AND status in (Open, Mitigating) ORDER BY priority DESC` — name it `Risk Register — [Programme]`
- **Dashboard gadgets:** (a) Issue Statistics on `ip-risk` filter by Status — shows how many open vs mitigated, (b) Filter Results showing top open risks by priority
- Extend the RO risk crawler script to run against all active programme projects, not just DPW — posts weekly digest to the programme's Slack channel

---

#### 12. Cross-Programme Dependency Register

| | |
|---|---|
| **Stage** | Delivery (primary), Go-Live (reference) |
| **Purpose** | Tracks dependencies between IP programmes and other P&T initiatives; flags where one programme blocks or is blocked by another |
| **Owner** | IP Director |
| **Format** | Notion / Jira |
| **Example** | No dedicated example found — cross-programme blockers currently surface ad-hoc in #ip-manage |

**Assessment:** Frequent source of go-live surprises. The RAID log covers intra-programme dependencies; cross-programme blockers have no formal home. Owned at IP Director level, not per-IPM.

**What to change:**
- Use Jira **issue links** of type "is blocked by" / "blocks" between epics in different programme projects — this is built-in Jira functionality
- **JQL to surface all cross-programme blocks:** `project in (DPW, [CROATIA-PROJECT], [WC-PROJECT]) AND issueType = Epic AND "Jira Link" = "is blocked by" AND status != Done` — saved as `Cross-Programme Blockers` filter; add as a gadget on the IP Director's dashboard
- **Notion summary page** (IP Director-owned): a single page with a manually-maintained table of known cross-programme dependencies, linked to the Jira epics. Updated at each SteerCo. This is the exception to the Jira-first rule — a narrative summary is useful here because the context matters, not just the link.

---

#### 13. All Areas Update

| | |
|---|---|
| **Stage** | Delivery (primary), Go-Live (reference) |
| **Purpose** | Cross-area status report aggregating progress by workstream |
| **Owner** | IPM |
| **Format** | Notion / Slack |
| **Example** | [IP Update — All Areas — 12 May](https://www.notion.so/35d032f852c580c0b28ceafc9bdb043a) · [21 Apr](https://www.notion.so/348032f852c58001a38bfdbef08b52df) · [05 May](https://www.notion.so/356032f852c5801aaa4fdf755c1aeb34) — weekly format currently in use |

**Assessment:** IPM manually queries squad leads who manually summarise their Jira boards into a narrative — double-handling of data that already exists in Jira. The Notion pages above show the current weekly format.

**What to change:**
- For each workstream/component, create a **JQL template**: `project = [PROGRAMME] AND component = "[WORKSTREAM]" AND updated >= -7d` → run to get: total issues, % in Done, open blockers (`labels = "ip-blocker"`), items completed this week, items added this week
- Build a **Claude prompt template** that takes the JQL output for each workstream and generates the standard "workstream update" paragraph
- IPM runs the prompt, reviews the output (2 min per workstream), adds exceptions and narrative, publishes to Notion and Slack
- Writing time drops from ~90 minutes to ~15 minutes; the quantitative data is always accurate
- The Notion page structure (one page per update, linked from the programme hub) stays — only the creation method changes

---

#### 14. SteerCo Deck

| | |
|---|---|
| **Stage** | Delivery (primary), Hypercare (reference) |
| **Purpose** | Steering Committee presentation — programme status, risks, decisions required |
| **Owner** | IP Director / IPM |
| **Format** | Notion / Slides |
| **Example** | No Notion example found — likely in Google Slides (not indexed) |

**Assessment:** IPM rebuilds Jira data as slide narrative each fortnight; content is stale within hours of being written.

**What to change:**
- Define a **standard SteerCo template** with three fixed data sections and one narrative section:
  - Section 1 — Programme RAG: pull from Pulse Check DB (artefact 15) — one row per programme, `RAG Status` field
  - Section 2 — Open risks: JQL `labels = "ip-risk" AND status in (Open, Mitigating) AND priority in (Blocker, Critical)` — IPM pastes the count and top 3 into the slide
  - Section 3 — Milestone status: Jira timeline screenshot or live Jira roadmap link embedded in slides
  - Section 4 — Decisions required: Jira filter `labels = "ip-decision" AND status = "Awaiting Decision"` — IPM lists these manually (few items, high context)
- The cultural shift: SteerCo attendees navigate to the live Jira dashboard for data questions; the deck is only for decisions-needed and narrative framing

---

#### 15. Pulse Check

| | |
|---|---|
| **Stage** | Delivery (primary), Hypercare (primary) |
| **Purpose** | Regular structured health check — RAG, morale, blockers |
| **Owner** | IPM |
| **Format** | Notion |
| **Example** | Greece Hypercare ran daily pulse checks (calendar: "Greek Hypercare — Daily Pulse Check") — no persistent Notion DB found; currently ad-hoc |

**Assessment:** Free-form text fields make it impossible to trend pulse checks or compare across programmes.

**What to change:**
- Create a **Notion database** `IP Pulse Checks` with these properties: `Programme` (select), `Date` (date), `RAG` (select: 🟢 Green / 🟡 Amber / 🔴 Red), `Morale` (select: 1–5), `Top Blocker` (text), `Blocker Owner` (person), `Action` (text), `Action Owner` (person), `Due` (date)
- Each pulse check = one row; takes 2 minutes to fill in
- **Views to create:** (a) Gallery view grouped by Programme showing current RAG as card colour, (b) Table view filtered to last 30 days for trend analysis, (c) Filter `RAG = Red OR Morale <= 2` for IP Director's escalation view
- Blocker items with an `Action Owner` are automatically candidates for a Jira task — IPM creates the Jira task and links the pulse check row to it

---

### Go-Live

---

#### 16. Go-Live Checklist / Readiness Assessment

| | |
|---|---|
| **Stage** | Delivery (built), Go-Live (executed) |
| **Purpose** | Formal sign-off gate; all items completed or derogated before launch |
| **Owner** | IPM + Squad Leads |
| **Format** | Notion |
| **Example** | [OM-2460: On-Call Checklist (Jira)](https://axilis.atlassian.net/browse/OM-2460) — example of checklist-as-Jira-tasks in use elsewhere in P&T |

**Assessment:** Static Notion checklist where "status" means "read the page." No enforcement, no live readiness %, no assignee accountability.

**What to change:**
- Create a **"Go-Live Gate" epic** in the programme's Jira project (e.g., `DPW-XX: RO Migration — Go-Live Gate`)
- Create one **Jira sub-task** per checklist item with: Assignee (squad lead responsible), Due date (go-live date minus buffer), Label per category: `glc-technical`, `glc-compliance`, `glc-commercial`, `glc-ops`, `glc-comms`
- **JQL readiness view:** `parent = [GO-LIVE-GATE-EPIC] ORDER BY labels ASC, status ASC` — shows all items grouped by category
- **Dashboard gadgets:** (a) Issue Statistics on Go-Live Gate epic by Status — shows readiness % live, (b) Filter Results for `parent = [GO-LIVE-GATE-EPIC] AND status != Done` — open items only
- Derogations: add a `glc-derogated` label to items approved to proceed as-is; add a Jira comment recording who approved the derogation and why
- The Notion checklist page is archived; IPM shares the Jira epic URL with stakeholders for readiness questions

---

#### 17. Regression Test Results

| | |
|---|---|
| **Stage** | Delivery (run), Go-Live (gate) |
| **Purpose** | Evidence that regression testing passed before go-live |
| **Owner** | QA / Squad Leads |
| **Format** | Chase / Notion |
| **Example** | No dedicated Notion page found — results currently shared ad-hoc in Slack |

**Assessment:** Chase test results exist but aren't surfaced in the programme view. IPM has to ask "have regression results been shared?" at every go-live — this is a manual chase.

**What to change:**
- Add a **Go-Live Gate sub-task** for regression sign-off (see artefact 16): `[PROGRAMME] Regression Testing — [Squad]`, assigned to QA lead, labelled `glc-technical`
- When QA completes, they: (a) close the Jira sub-task, (b) add a **remote issue link** on the Go-Live Gate epic pointing to the Chase test run — link type "tested by"
- The Chase test run URL in the remote link gives IPM and IP Director one-click access to the full test results from the Jira epic
- Regression pass/fail is visible in the Go-Live Gate readiness view without anyone sending a message

---

#### 18. Go/No-Go Decision Record

| | |
|---|---|
| **Stage** | Go-Live |
| **Purpose** | Formal record of launch decision and who approved |
| **Owner** | IP Director |
| **Format** | Notion |
| **Example** | Closest example: [Slack — Yentel "WE ARE GOOD TO GO" (Belgium, Sep 2024)](https://superbet.slack.com/archives/C06HULLL8DT/p1725262802826589) — currently a Slack message, not a formal record |

**Assessment:** Currently an informal Slack message or Notion paragraph with no enforcement and no queryable audit trail.

**What to change:**
- Create a **"Go/No-Go Decision" sub-task** on the Go-Live Gate epic (artefact 16), labelled `glc-gng`, assigned to IP Director
- When approved, IP Director closes the task with a comment containing: approver names, decision (Go / No-Go / Conditional Go), any conditions or derogations outstanding, decision timestamp
- **Soft gate (TPM-owned):** add a "is blocked by" link from the programme epic to this task — Jira shows the block but doesn't prevent transition; IPM must manually check it's closed before proceeding
- **Hard gate (requires Jira admin):** create a workflow rule that prevents transitioning the programme epic to "Live" status unless all `glc-*` labelled sub-tasks are closed — raise with Jira admin as a separate workstream

---

### Hypercare

---

#### 19. Hypercare Report

| | |
|---|---|
| **Stage** | Hypercare |
| **Purpose** | Daily/weekly status on post-launch issues, resolution tracking, escalation log |
| **Owner** | IPM |
| **Format** | Notion |
| **Example** | [Transact / Greece Hypercare Triage — meeting notes](https://docs.google.com/document/d/1ZVB1jI8ofWZfq9hTcjSNtlrGHoqcOKDoqvPRqMg4yFc) (Google Docs) |

**Assessment:** IPM manually assembles narrative from Jira, Chase, and Grafana at the highest-stress phase of delivery. This is where manual overhead is most painful and most avoidable.

**What to change:**
- Define standard **JQL for hypercare:** `project = [PROGRAMME] AND labels = "ip-post-launch" AND created >= [go-live date]` — broken down by priority: `AND priority in (Blocker, Critical)` for P1/P2 count
- Define a **Chase query** for post-launch P1/P2 tickets linked to the programme
- Build a **Claude prompt template** that takes: (a) Jira output for the above JQL, (b) Chase P1/P2 count, (c) Grafana uptime % (manual paste or API) → outputs the standard hypercare report table: open issues by severity, resolution rate vs prior day, uptime, SLA compliance
- IPM adds one paragraph: what's been escalated, what's been resolved, what needs SteerCo attention
- Publish to the programme's Notion hub page and Slack channel
- Total time: ~10 minutes to run the prompt and add narrative vs ~45 minutes manual

---

#### 20. Issue Log

| | |
|---|---|
| **Stage** | Hypercare |
| **Purpose** | Tracks live defects and operational issues post-launch |
| **Owner** | IPM + Dev |
| **Format** | Chase / Notion |
| **Example** | No Notion page found — issues tracked in Chase, Notion re-entry by IPM |

**Assessment:** Classic double-entry: Chase for devs, Notion re-entry for IPM. Produces a Notion page that's always slightly out of date.

**What to change:**
- **Eliminate the Notion copy entirely**
- **JQL saved filter:** `project = [PROGRAMME] AND labels = "ip-post-launch" AND status != Done ORDER BY priority DESC, created DESC` — name it `Issue Log — [Programme] Post-Launch`; share with IPM and IP Director as the authoritative view
- For Chase issues: squad leads add a **remote issue link** from the Chase ticket to the programme's post-launch epic in Jira (link type: "is caused by" or "relates to"). This gives IPM a single Jira view that includes Chase-originated issues without re-entering them.
- **Jira board:** create a Kanban board filtered to the above JQL — IPM uses this board as the issue log view; no separate Notion page needed

---

### Aftercare

---

#### 21. Retrospective / Lessons Learned

| | |
|---|---|
| **Stage** | Aftercare |
| **Purpose** | What went well, what didn't, and what to carry forward |
| **Owner** | IPM + Team |
| **Format** | Notion |
| **Example** | [Player — Greece Post-Launch Retro (Google Docs)](https://docs.google.com/document/d/12UufUHn-T9vP_zjuxP0oca3ZA0ogWXUGVwjPRWsEV4s) — retro notes from Greece launch |

**Assessment:** Action items are written and forgotten. The problem is accountability and follow-up, not the format of the document.

**What to change:**
- Use a **standard Notion retro template** with four mandatory sections: What went well / What didn't / What to change / Action items
- **Action items section:** each action item is entered directly as a Jira task (IPM creates during the retro, not after) with: assignee, due date (within 30 days of retro), label `ip-retro-action`
- **30-day follow-up checkpoint:** the retro creates one additional Jira task — `[Programme] Retro action review` — due 30 days after the retro date, assigned to IPM. At this task's due date, IPM runs: `labels = "ip-retro-action" AND project = [PROGRAMME] AND status != Done` to check completion rate.
- **Lessons database:** create an `IP Lessons Learned` Notion database with properties: `Programme` (select), `Category` (select: Process / Tooling / Stakeholder / Technical / Resourcing / Go-Live), `Lesson` (title), `Impact` (select: Low / Medium / High), `Applied in next programme?` (checkbox). Each lesson = one row. Over time this becomes a queryable knowledge base across all programmes.

---

#### 22. Programme Closure Report

| | |
|---|---|
| **Stage** | Aftercare |
| **Purpose** | Formal close-out — outcomes vs objectives, handover notes, final cost/timeline |
| **Owner** | IP Director |
| **Format** | Notion |
| **Example** | No example found — not consistently produced across programmes |

**Assessment:** High-effort document written when team attention is already elsewhere. Most of the quantitative data already exists in Jira and should be auto-populated.

**What to change:**
- Define a **standard closure report template** in Notion with these auto-populated vs manual sections:
  - **Auto-populated from Jira** (IPM runs JQL and pastes): planned vs actual go-live date (from epic history), total epics delivered, total issues raised post-launch, open vs closed at closure date, milestone variance (due dates vs actual close dates), sprint velocity trend
  - **Manual (IPM writes):** scope delivered vs committed, key decisions and rationale, what was derogated and why, handover notes (who now owns ongoing operations), budget actuals vs plan
  - **Manual (IP Director writes):** overall outcome assessment, strategic learnings, recommendation for future similar programmes
- With auto-populated sections, IPM effort drops from ~1 day to ~2 hours
- Closure report is linked to the programme's Jira epic as a remote link; the epic is then closed, completing the programme lifecycle in Jira

---

## Applicability by Programme Type

| Artefact | Market Entry | Platform Migration | Cross-Area Product |
|---|:---:|:---:|:---:|
| Scoping Document | ✓ | ✓ | ✓ |
| AML Risk Derivation Matrix | ✓ | — | Conditional |
| Feature Readiness Overview | ✓ | ✓ | ✓ |
| Stakeholder Map / RACI | ✓ | ✓ | ✓ |
| Q&A / Open Questions Register | ✓ | ✓ | ✓ |
| Communications Plan | ✓ | Conditional | Conditional |
| Programme Calendar | ✓ | ✓ | ✓ |
| Decision Log | ✓ | ✓ | ✓ |
| Budget / Cost Tracker | ✓ | ✓ | Conditional |
| Risk Register / RAID Log | ✓ | ✓ | ✓ |
| Cross-Programme Dependency Register | ✓ | ✓ | ✓ |
| All Areas Update | ✓ | ✓ | ✓ |
| SteerCo Deck | ✓ | ✓ | ✓ |
| Pulse Check | ✓ | ✓ | ✓ |
| Go-Live Checklist | ✓ | ✓ | ✓ |
| Regression Test Results | ✓ | ✓ | ✓ |
| Go/No-Go Decision Record | ✓ | ✓ | ✓ |
| Hypercare Report | ✓ | ✓ | ✓ |
| Issue Log | ✓ | ✓ | ✓ |
| Retrospective / Lessons Learned | ✓ | ✓ | ✓ |
| Programme Closure Report | ✓ | ✓ | ✓ |
| IP Scoping Process | ref | ref | ref |
