---
name: Local Run Notes
description: Architecture notes for running the crawler locally vs via GitHub Actions
type: reference
project: RO Migration to Betler
---

# RO Risk Crawler — Local Run Notes

## Run history
- Runs 1–13 (2026-05-01 to 2026-05-21): all executed as Claude Code MCP sessions, NOT via crawler.py
- GitHub Actions workflow exists (`.github/workflows/ro-risk-crawler.yml`) but has not produced any commits yet (as of run 13)
- `risk-register.json` is not committed to git — local file is 13 runs ahead of the remote

## Architecture

| Mode | How it runs | When |
|---|---|---|
| Claude Code MCP session | Claude uses Jira/Slack/Notion MCP tools directly | Local / ad-hoc runs |
| GitHub Actions (`crawler.py`) | Anthropic SDK agent loop, REST APIs, cron Monday 09:00 UTC | Automated weekly |

## Running crawler.py locally

Requires these env vars (not set at system level — no `.env` file in project):

| Var | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic SDK |
| `JIRA_EMAIL` | Jira REST auth |
| `JIRA_API_TOKEN` | Jira REST auth |
| `SLACK_BOT_TOKEN` | Slack REST API |
| `NOTION_API_KEY` | Notion REST API |

Python 3.13 installed. `anthropic` and `requests` packages available (`pip install -r requirements.txt`).

> **Windows note**: check env vars with PowerShell (`$env:VAR_NAME`), not bash `%VAR%` syntax.

## Before the first GitHub Actions run

The remote `risk-register.json` is stale (run 1 state). Before Monday's automated run, commit the current local register so the workflow starts from run 13 state — otherwise it will re-detect all 35 risks as new and re-post Jira comments.

Last updated: 2026-05-22
