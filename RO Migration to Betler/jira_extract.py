"""
jira_extract.py — Generic Jira API response file processor for RO Migration runs.

Usage:
  python jira_extract.py <response.json> [--fields key,summary,status,updated,prd,health,ssu,labels]
                         [--epics] [--filter-key KEYS] [--filter-status STATUSES]

Input formats accepted:
  {"issues": {"nodes": [...]}}   — Atlassian MCP search format
  {"issues": [...]}              — flat issues wrapper
  [...]                          — bare list
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

FIELD_ALIASES = {
    "prd":    "customfield_12114",
    "health": "customfield_12111",
    "ssu":    "customfield_14447",
}

DEFAULT_FIELDS = ["key", "summary", "status", "updated", "prd", "health", "ssu", "labels"]


def _load_issues(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        issues = raw.get("issues", raw)
        if isinstance(issues, list):
            return issues
        if isinstance(issues, dict):
            return issues.get("nodes", [])
    raise ValueError(f"Unrecognised input format in {path}")


def _adf_to_text(node):
    """Recursively extract plain text from an Atlassian Document Format node."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return " ".join(_adf_to_text(n) for n in node if n)
    if not isinstance(node, dict):
        return ""
    t = node.get("type", "")
    if t == "text":
        return node.get("text", "")
    if t in ("hardBreak", "rule"):
        return " "
    content = node.get("content", [])
    parts = [_adf_to_text(c) for c in (content or [])]
    sep = " " if t in ("paragraph", "heading", "listItem") else ""
    return sep.join(p for p in parts if p)


def _get_field(issue, field_name):
    """Resolve a field name (alias or direct) from an issue dict."""
    fields = issue.get("fields", issue)
    resolved = FIELD_ALIASES.get(field_name, field_name)

    if field_name == "key":
        return issue.get("key", fields.get("key", ""))

    if field_name == "status":
        st = fields.get("status", {})
        if isinstance(st, dict):
            return st.get("name", "")
        return str(st) if st else ""

    if field_name == "updated":
        raw = fields.get("updated", "")
        if raw:
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return raw[:10]
        return ""

    if field_name == "labels":
        lbs = fields.get("labels", [])
        return ", ".join(lbs) if lbs else ""

    if field_name == "summary":
        return fields.get("summary", "")

    if field_name == "ssu":
        val = fields.get(resolved, fields.get(field_name))
        if val is None:
            return ""
        if isinstance(val, dict) and "type" in val:
            text = _adf_to_text(val).strip()
            return re.sub(r"\s+", " ", text)
        if isinstance(val, str):
            return val
        return str(val)

    if field_name in ("prd", "health"):
        val = fields.get(resolved, fields.get(field_name))
        if isinstance(val, dict):
            return val.get("value", val.get("name", ""))
        return str(val) if val is not None else ""

    # Generic fallback
    val = fields.get(resolved, fields.get(field_name))
    if isinstance(val, dict):
        return val.get("value", val.get("name", val.get("key", "")))
    return str(val) if val is not None else ""


def _filter(issues, filter_keys, filter_statuses):
    if filter_keys:
        keys_upper = {k.upper() for k in filter_keys}
        issues = [i for i in issues if i.get("key", "").upper() in keys_upper]
    if filter_statuses:
        statuses_lower = {s.lower() for s in filter_statuses}
        issues = [i for i in issues
                  if _get_field(i, "status").lower() in statuses_lower]
    return issues


def _col_widths(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    return widths


def _print_table(headers, rows):
    widths = _col_widths(headers, rows)
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*[str(c) for c in row]))


def cmd_default(issues, fields):
    headers = [f.upper() for f in fields]
    rows = []
    for issue in issues:
        row = [_get_field(issue, f) for f in fields]
        rows.append(row)
    _print_table(headers, rows)
    print(f"\n{len(issues)} issue(s)")


def cmd_epics(issues):
    """Print epic summary: KEY | STATUS | UPDATED | SUMMARY, plus status breakdown."""
    headers = ["KEY", "STATUS", "UPDATED", "SUMMARY"]
    rows = []
    status_counts = {}
    for issue in issues:
        key = _get_field(issue, "key")
        status = _get_field(issue, "status")
        updated = _get_field(issue, "updated")
        summary = _get_field(issue, "summary")
        rows.append([key, status, updated, summary[:60]])
        status_counts[status] = status_counts.get(status, 0) + 1

    _print_table(headers, rows)
    print(f"\n{len(issues)} epic(s)")
    print("\nStatus breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status:<25} {count}")


def main():
    parser = argparse.ArgumentParser(description="Process a saved Jira API response file.")
    parser.add_argument("file", help="Path to saved Jira API response JSON")
    parser.add_argument(
        "--fields",
        default=",".join(DEFAULT_FIELDS),
        help="Comma-separated field names (supports aliases: prd, health, ssu)"
    )
    parser.add_argument(
        "--epics",
        action="store_true",
        help="Show epic summary with status breakdown"
    )
    parser.add_argument(
        "--filter-key",
        nargs="+",
        metavar="KEY",
        help="Only show issues with these Jira keys"
    )
    parser.add_argument(
        "--filter-status",
        nargs="+",
        metavar="STATUS",
        help="Only show issues with these statuses (case-insensitive)"
    )
    args = parser.parse_args()

    try:
        issues = _load_issues(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    issues = _filter(issues, args.filter_key, args.filter_status)

    if args.epics:
        cmd_epics(issues)
    else:
        fields = [f.strip() for f in args.fields.split(",") if f.strip()]
        cmd_default(issues, fields)


if __name__ == "__main__":
    main()
