"""
Tool implementations: Jira REST API, Slack Web API, Notion API, and write_risk_register.
Each function is invoked by the agent loop when Claude requests a tool call.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

JIRA_BASE = "https://axilis.atlassian.net"
JIRA_AUTH = (
    os.environ.get("JIRA_EMAIL", ""),
    os.environ.get("JIRA_API_TOKEN", ""),
)
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
RISK_REGISTER_PATH = Path(__file__).parent / "risk-register.json"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(url: str, *, auth=None, headers: dict = None, params: dict = None) -> dict:
    h = headers or {}
    for attempt in range(3):
        r = requests.get(url, auth=auth, headers=h, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"GET {url} failed after retries")


def _post(url: str, *, auth=None, headers: dict = None, data: dict = None) -> dict:
    h = headers or {}
    for attempt in range(3):
        r = requests.post(url, auth=auth, headers=h, json=data, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json() if r.content else {}
    raise RuntimeError(f"POST {url} failed after retries")


def _put(url: str, *, auth=None, headers: dict = None, data: dict = None) -> dict:
    h = headers or {}
    r = requests.put(url, auth=auth, headers=h, json=data, timeout=30)
    r.raise_for_status()
    return {}


def _patch(url: str, *, headers: dict = None, data: dict = None) -> dict:
    h = headers or {}
    r = requests.patch(url, headers=h, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Jira
# ---------------------------------------------------------------------------

_JIRA_HEADERS = {"Accept": "application/json"}
_JIRA_JSON_HEADERS = {**_JIRA_HEADERS, "Content-Type": "application/json"}


def searchJiraIssuesUsingJql(
    jql: str,
    fields: str = None,
    maxResults: int = 50,
    startAt: int = 0,
) -> dict:
    params: dict[str, Any] = {"jql": jql, "maxResults": maxResults, "startAt": startAt}
    if fields:
        params["fields"] = fields
    return _get(
        f"{JIRA_BASE}/rest/api/3/search",
        auth=JIRA_AUTH,
        headers=_JIRA_HEADERS,
        params=params,
    )


def getJiraIssue(issueKey: str, fields: str = None) -> dict:
    params = {}
    if fields:
        params["fields"] = fields
    return _get(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}",
        auth=JIRA_AUTH,
        headers=_JIRA_HEADERS,
        params=params or None,
    )


def editJiraIssue(issueKey: str, fields: dict = None, update: dict = None) -> dict:
    body: dict = {}
    if fields:
        body["fields"] = fields
    if update:
        body["update"] = update
    _put(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}",
        auth=JIRA_AUTH,
        headers=_JIRA_JSON_HEADERS,
        data=body,
    )
    return {"success": True}


def addCommentToJiraIssue(issueKey: str, body: str) -> dict:
    return _post(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}/comment",
        auth=JIRA_AUTH,
        headers=_JIRA_JSON_HEADERS,
        data={
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body}],
                    }
                ],
            }
        },
    )


def getTransitionsForJiraIssue(issueKey: str) -> dict:
    return _get(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}/transitions",
        auth=JIRA_AUTH,
        headers=_JIRA_HEADERS,
    )


def transitionJiraIssue(issueKey: str, transitionId: str) -> dict:
    _post(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}/transitions",
        auth=JIRA_AUTH,
        headers=_JIRA_JSON_HEADERS,
        data={"transition": {"id": str(transitionId)}},
    )
    return {"success": True}


def getJiraIssueRemoteIssueLinks(issueKey: str) -> dict:
    return _get(
        f"{JIRA_BASE}/rest/api/3/issue/{issueKey}/remotelink",
        auth=JIRA_AUTH,
        headers=_JIRA_HEADERS,
    )


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------

_SLACK_BASE = "https://slack.com/api"


def _slack_headers() -> dict:
    return {"Authorization": f"Bearer {SLACK_TOKEN}"}


def _slack_post(method: str, **kwargs) -> dict:
    data = _post(f"{_SLACK_BASE}/{method}", headers=_slack_headers(), data=kwargs)
    if not data.get("ok"):
        raise RuntimeError(f"Slack {method}: {data.get('error')}")
    return data


def slack_read_channel(channelId: str, oldest: float = None, limit: int = 100) -> dict:
    params: dict[str, Any] = {"channel": channelId, "limit": limit}
    if oldest is not None:
        params["oldest"] = str(oldest)
    return _slack_post("conversations.history", **params)


def slack_read_thread(channelId: str, threadTs: str) -> dict:
    return _slack_post("conversations.replies", channel=channelId, ts=threadTs)


def slack_search_public_and_private(query: str, count: int = 20) -> dict:
    return _slack_post("search.messages", query=query, count=count)


def slack_send_message(channelId: str, text: str) -> dict:
    return _slack_post("chat.postMessage", channel=channelId, text=text)


def slack_search_channels(query: str, limit: int = 50) -> dict:
    # Fetch up to 1000 channels and filter by name substring
    data = _slack_post(
        "conversations.list", limit=200, types="public_channel,private_channel"
    )
    matched = [
        c
        for c in data.get("channels", [])
        if query.lower() in c.get("name", "").lower()
    ]
    return {"ok": True, "channels": matched[:limit]}


def slack_get_user_profile(userId: str) -> dict:
    return _slack_post("users.profile.get", user=userId)


# ---------------------------------------------------------------------------
# Notion
# ---------------------------------------------------------------------------

_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def _notion_id(url_or_id: str) -> str:
    """Extract a Notion page/database ID from a URL or collection:// URI."""
    import re

    s = url_or_id.strip().rstrip("/")
    # collection://uuid
    if s.startswith("collection://"):
        return s.replace("collection://", "")
    # bare UUID (with or without dashes)
    if re.fullmatch(r"[a-f0-9\-]{32,36}", s):
        return s
    # URL: grab last path segment that looks like a UUID
    match = re.search(r"([a-f0-9]{32}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", s)
    if match:
        return match.group(1)
    return s  # fall back to passing through as-is


def notion_fetch(url: str) -> dict:
    nid = _notion_id(url)
    # Try page first, fall back to database
    try:
        return _get(f"{_NOTION_BASE}/pages/{nid}", headers=_NOTION_HEADERS)
    except requests.HTTPError:
        return _get(f"{_NOTION_BASE}/databases/{nid}", headers=_NOTION_HEADERS)


def notion_query_data_sources(
    data_source_id: str,
    filter: dict = None,
    sorts: list = None,
    page_size: int = 50,
) -> dict:
    db_id = _notion_id(data_source_id)
    body: dict = {"page_size": page_size}
    if filter:
        body["filter"] = filter
    if sorts:
        body["sorts"] = sorts
    return _post(f"{_NOTION_BASE}/databases/{db_id}/query", headers=_NOTION_HEADERS, data=body)


def notion_query_meeting_notes(
    data_source_id: str,
    filter: dict = None,
    sorts: list = None,
    page_size: int = 50,
) -> dict:
    # Same implementation as query_data_sources; separate tool name matches MCP naming
    return notion_query_data_sources(data_source_id, filter=filter, sorts=sorts, page_size=page_size)


def notion_search(query: str, filter_type: str = None, page_size: int = 20) -> dict:
    body: dict = {"query": query, "page_size": page_size}
    if filter_type:
        body["filter"] = {"value": filter_type, "property": "object"}
    return _post(f"{_NOTION_BASE}/search", headers=_NOTION_HEADERS, data=body)


def notion_create_pages(parent_id: str, properties: dict, children: list = None) -> dict:
    body: dict = {
        "parent": {"database_id": _notion_id(parent_id)},
        "properties": properties,
    }
    if children:
        body["children"] = children
    return _post(f"{_NOTION_BASE}/pages", headers=_NOTION_HEADERS, data=body)


def notion_update_page(pageId: str, properties: dict) -> dict:
    return _patch(
        f"{_NOTION_BASE}/pages/{_notion_id(pageId)}",
        headers=_NOTION_HEADERS,
        data={"properties": properties},
    )


def notion_get_comments(blockId: str) -> dict:
    return _get(
        f"{_NOTION_BASE}/comments",
        headers=_NOTION_HEADERS,
        params={"block_id": _notion_id(blockId)},
    )


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def write_risk_register(data: dict) -> dict:
    RISK_REGISTER_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {"success": True, "path": str(RISK_REGISTER_PATH)}


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

TOOL_DISPATCH = {
    # Jira
    "searchJiraIssuesUsingJql": searchJiraIssuesUsingJql,
    "getJiraIssue": getJiraIssue,
    "editJiraIssue": editJiraIssue,
    "addCommentToJiraIssue": addCommentToJiraIssue,
    "getTransitionsForJiraIssue": getTransitionsForJiraIssue,
    "transitionJiraIssue": transitionJiraIssue,
    "getJiraIssueRemoteIssueLinks": getJiraIssueRemoteIssueLinks,
    # Slack
    "slack_read_channel": slack_read_channel,
    "slack_read_thread": slack_read_thread,
    "slack_search_public_and_private": slack_search_public_and_private,
    "slack_send_message": slack_send_message,
    "slack_search_channels": slack_search_channels,
    "slack_get_user_profile": slack_get_user_profile,
    # Notion
    "notion_fetch": notion_fetch,
    "notion_query_data_sources": notion_query_data_sources,
    "notion_query_meeting_notes": notion_query_meeting_notes,
    "notion_search": notion_search,
    "notion_create_pages": notion_create_pages,
    "notion_update_page": notion_update_page,
    "notion_get_comments": notion_get_comments,
    # State
    "write_risk_register": write_risk_register,
}


def execute_tool(name: str, inputs: dict) -> Any:
    fn = TOOL_DISPATCH.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(**inputs)
    except Exception as exc:
        return {"error": str(exc)}
