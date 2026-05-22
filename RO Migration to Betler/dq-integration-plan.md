# Plan: Route RO Crawler 'Not Closed Out' Findings into Player DQ Workflow via Jira Label

## Context

The RO Risk Crawler's Epic Context Check classifies some PLAYER initiatives as `not_closed_out` — initiatives where the release date has passed and all child epics are Done/Won't Do, but the initiative itself is still open in Jira. These are data quality issues, not risks.

The Player Jira Data Quality workflow already audits PLAYER initiatives and notifies squad leads weekly. Rather than building a separate notification path, we route the crawler's `not_closed_out` findings into the existing DQ workflow via a Jira label (`ro-not-closed-out`). The DQ workflow reads the label, appends a note to the relevant squad's Slack message, then clears all labels at end of run so the next Monday's crawler stamps a fresh, accurate set.

---

## Approach

**Jira label as handoff mechanism.** The crawler stamps `ro-not-closed-out` on each flagged initiative every Monday. The DQ workflow detects the label (via JQL), appends a note per squad, and removes all labels at end of run. No intermediate files, no Jira side-effects that persist beyond one week.

---

## Changes to `romania-risk-crawler.md`

### 1. Add a new "DQ Integration" section

Inserted after the "Dependency Handling" section.

### 2. Add Step 1d to Implementation Approach

Inserted after Step 1c, before Step 1a:

> For every initiative classified as `not_closed_out` in Step 1c, stamp the label `ro-not-closed-out` via `editJiraIssue`. In the same step, remove the label from any PLAYER initiative that had it but is no longer `not_closed_out` this run.

---

## Changes to `player-jira-data-quality-workflow.md`

### 1. Step 2b — Read RO crawler labels

Inserted after Step 2, before Step 3. Queries:
```
project = PLAYER AND issuetype = Initiative AND labels = "ro-not-closed-out"
```
Stores results as `ro_not_closed_out`.

### 2. Step 4 — Squad Slack messages

Modified both the "has gaps" and "zero gaps" templates:
- If a squad has gaps AND RO labels: RO block appended after the gap list
- If a squad has zero gaps AND RO labels: celebration replaced with a modified message that includes the RO block

### 3. Step 9 — Remove RO Migration labels

Added as the final step after Step 8. Fires all label-removal calls in parallel. Non-blocking — failures are logged and skipped. Count of labels cleared is included in the Step 8 summary to Jonathan.

---

## Files Modified

| File | Changes |
|---|---|
| `romania-risk-crawler.md` | Added "DQ Integration" section; added Step 1d to Implementation Approach |
| `player-jira-data-quality-workflow.md` | Added Step 2b; modified Step 4 squad message templates; added Step 9; updated Step 8 summary |

---

## Verification (completed)

- [x] Step 1d is in the correct position (after 1c, before 1a)
- [x] Step 2b JQL uses `labels = "ro-not-closed-out"` (not `in`)
- [x] Step 4 handles the "no field gaps but has RO label" case
- [x] Step 9 fires after Step 8 and is non-blocking
- [x] Step 8 summary includes `RO Migration labels cleared: X initiatives`
