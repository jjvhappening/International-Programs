---
name: Notion Risk Register Schema Reference
description: Column names, data source ID, and option values for the RO Migration Risk Register Notion database — use to avoid schema fetch round-trips at run start
type: reference
project: RO Migration to Betler
---

# Notion Risk Register Schema

**Data source ID**: `collection://7f410211-1a06-4fcc-b10c-ab58571a781a`
**Notion DB URL**: https://www.notion.so/9dab74b2885b4f8f93aa73dad97ea6da

> ⚠️ The title column is named `"Risk ID"` — NOT `"title"`. Always use `"Risk ID"` in SQL queries.

> 🚨 **CRITICAL:** The Jira key column is named **`"Jira Initiative"`** — NOT `"Jira Key"`. Querying `"Jira Key"` returns zero results. This caused a lookup failure in Run 12 (2026-05-20) before this file was correctly loaded. The path was previously wrong (`JonathanVince` → now fixed to `JonVince`).

## SQLite Table Definition

```sql
CREATE TABLE IF NOT EXISTS "collection://7f410211-1a06-4fcc-b10c-ab58571a781a" (
    url TEXT UNIQUE,
    createdTime TEXT,
    "Suppressed" TEXT,          -- "__YES__" = true, "__NO__" = false
    "Signals" TEXT,
    "Trend" TEXT,               -- "Worsening" | "Stable" | "Improving"
    "Workstream" TEXT,          -- "IP" | "GAM" | "DAP" | "PLT" | "PLAYER" | "SOC" | cross-cutting/compliance risks with no single board → use "IP"
    "Days to Release" FLOAT,
    "Mitigation Status" TEXT,   -- "None" | "Planned" | "In Progress" | "Complete"
    "Jira Initiative" TEXT,
    "Slack Evidence" TEXT,
    "Status" TEXT,              -- "Open" | "Monitoring" | "Escalated" | "Resolved" | "Closed" | "Suppressed"
    "Severity" TEXT,            -- "High" | "Medium" | "Low"
    "Description" TEXT,
    "Category" TEXT,            -- "technical" | "timeline" | "scope" | "compliance" | "dependency" | "data_quality"
    "Risk ID" TEXT              -- this is the title/primary field
)
```

## Standard Query Pattern

```sql
SELECT url, "Risk ID", "Status", "Severity", "Days to Release"
FROM "collection://7f410211-1a06-4fcc-b10c-ab58571a781a"
WHERE "Risk ID" IN ('RR-001', 'RR-002', ...)
ORDER BY "Risk ID"
```

## 429 Rate Limiting Notes

- Notion queries will return 429 after 3–4 rapid sequential queries
- Space queries at least 2–3 seconds apart, or batch into a single SQL `IN` clause
- On 429: wait and retry once — errors are transient
- Prefer one broad query fetching all needed `Risk ID`s over multiple narrow queries

## Notion Update Tool

For `notion-update-page`, use command `"update_properties"` with:
- `properties`: JSON map of column name → value
- Do NOT include `content_updates` — it is not a parameter for `update_properties` (only for `update_content` command)

## Notion Batch Create

For creating new risk pages, use `notion-create-pages` with:
- `parent`: `{"type": "data_source_id", "data_source_id": "7f410211-1a06-4fcc-b10c-ab58571a781a"}`
- `pages`: array of page objects — accepts up to 100 pages per call; always batch rather than looping individually
- Each page object needs a `properties` map; `Risk ID` is the title field

Last updated: 2026-05-28
