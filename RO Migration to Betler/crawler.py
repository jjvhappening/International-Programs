"""
RO Migration Risk Crawler — Anthropic SDK agent loop.
Reads the spec + risk register, invokes Claude with tools, writes back the
updated register. Designed to run on GitHub Actions (Linux) on a weekly cron.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from tool_definitions import TOOL_DEFINITIONS
from tools import execute_tool

RISK_REGISTER_PATH = Path(__file__).parent / "risk-register.json"
SPEC_PATH = Path(__file__).parent / "romania-risk-crawler.md"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS_PER_TURN = 8192
# Safety cap — prevents runaway loops on unexpected Claude behaviour
MAX_TURNS = 80


def load_risk_register() -> dict:
    if RISK_REGISTER_PATH.exists():
        return json.loads(RISK_REGISTER_PATH.read_text(encoding="utf-8"))
    return {"last_run": None, "risks": [], "suggested_dependencies": []}


def build_system_prompt(spec: str, risk_register: dict, today: str) -> str:
    return f"""\
You are running the Romania Risk Crawler for the week of {today}.
Follow the spec below exactly, including the parallelisation strategy and context management guidelines.

IMPORTANT TOOL NOTES (differences from the MCP environment):
- Notion tools use underscores, not dashes: notion_fetch, notion_query_data_sources,
  notion_query_meeting_notes, notion_search, notion_create_pages, notion_update_page.
- notion_query_data_sources and notion_query_meeting_notes accept a `filter` dict in Notion
  API format, not SQL. Example date filter:
    {{"property": "Date", "date": {{"on_or_after": "2026-04-24"}}}}
- editJiraIssue accepts either `fields` (standard update) or `update` (atomic ops).
  To add/remove labels atomically without clobbering existing ones, use:
    update={{"labels": [{{"add": "ro-not-closed-out"}}]}}
- write_risk_register: call this at the very end with the complete updated register JSON.
  This is the only way the updated register is persisted.

---

{spec}

---

Current risk register (last_run: {risk_register.get("last_run", "never")}):
{json.dumps(risk_register, indent=2)}

Today's date: {today}
"""


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def run() -> None:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    risk_register = load_risk_register()
    spec = SPEC_PATH.read_text(encoding="utf-8")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    system = build_system_prompt(spec, risk_register, today)
    messages: list[dict] = [
        {"role": "user", "content": "Run the weekly RO migration risk crawl."}
    ]

    log(f"Starting crawl for {today} (register: {len(risk_register.get('risks', []))} risks)")

    turns = 0
    while turns < MAX_TURNS:
        turns += 1
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_PER_TURN,
            system=system,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Log usage every turn for cost tracking in GitHub Actions output
        usage = response.usage
        log(
            f"Turn {turns} | stop={response.stop_reason} | "
            f"in={usage.input_tokens} out={usage.output_tokens}"
        )

        if response.stop_reason == "end_turn":
            log("Crawl complete.")
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    log(f"  → {block.name}({json.dumps(block.input)[:300]})")
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                            if not isinstance(result, str)
                            else result,
                        }
                    )

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            log(f"Unexpected stop_reason: {response.stop_reason}", )
            sys.exit(1)
    else:
        log(f"ERROR: hit MAX_TURNS ({MAX_TURNS}) without completing — possible loop")
        sys.exit(1)


if __name__ == "__main__":
    run()
