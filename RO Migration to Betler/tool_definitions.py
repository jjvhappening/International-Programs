"""
Anthropic tool schemas for the RO Risk Crawler.
Tool names match the MCP tool names used in the spec (underscores for Notion).
"""

TOOL_DEFINITIONS = [
    # ------------------------------------------------------------------
    # Jira
    # ------------------------------------------------------------------
    {
        "name": "searchJiraIssuesUsingJql",
        "description": (
            "Search Jira issues using JQL. Always pass a fields parameter "
            "listing only the fields you need to avoid oversized responses. "
            "Use startAt for pagination."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "jql": {"type": "string"},
                "fields": {
                    "type": "string",
                    "description": (
                        "Comma-separated field list, e.g. "
                        "'key,summary,status,updated,customfield_12111'"
                    ),
                },
                "maxResults": {"type": "integer", "default": 50},
                "startAt": {"type": "integer", "default": 0},
            },
            "required": ["jql"],
        },
    },
    {
        "name": "getJiraIssue",
        "description": "Fetch a single Jira issue by key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "fields": {
                    "type": "string",
                    "description": "Comma-separated field list to return.",
                },
            },
            "required": ["issueKey"],
        },
    },
    {
        "name": "editJiraIssue",
        "description": (
            "Update a Jira issue. Use `fields` for standard field updates. "
            "Use `update` for atomic label operations without clobbering "
            "existing labels, e.g. update={\"labels\": [{\"add\": \"my-label\"}]}."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "fields": {
                    "type": "object",
                    "description": "Standard field update map.",
                },
                "update": {
                    "type": "object",
                    "description": "Atomic update operations, e.g. label add/remove.",
                },
            },
            "required": ["issueKey"],
        },
    },
    {
        "name": "addCommentToJiraIssue",
        "description": "Post a comment to a Jira issue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "body": {"type": "string", "description": "Plain text comment body."},
            },
            "required": ["issueKey", "body"],
        },
    },
    {
        "name": "getTransitionsForJiraIssue",
        "description": "Get available workflow transitions for a Jira issue.",
        "input_schema": {
            "type": "object",
            "properties": {"issueKey": {"type": "string"}},
            "required": ["issueKey"],
        },
    },
    {
        "name": "transitionJiraIssue",
        "description": "Transition a Jira issue to a new status using a transition ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "transitionId": {"type": "string"},
            },
            "required": ["issueKey", "transitionId"],
        },
    },
    {
        "name": "getJiraIssueRemoteIssueLinks",
        "description": "Get remote issue links (external links) on a Jira issue.",
        "input_schema": {
            "type": "object",
            "properties": {"issueKey": {"type": "string"}},
            "required": ["issueKey"],
        },
    },
    # ------------------------------------------------------------------
    # Slack
    # ------------------------------------------------------------------
    {
        "name": "slack_read_channel",
        "description": "Read message history from a Slack channel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelId": {"type": "string"},
                "oldest": {
                    "type": "number",
                    "description": "Unix timestamp — only return messages after this time.",
                },
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["channelId"],
        },
    },
    {
        "name": "slack_read_thread",
        "description": "Read all replies in a Slack thread.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelId": {"type": "string"},
                "threadTs": {"type": "string", "description": "Thread parent timestamp."},
            },
            "required": ["channelId", "threadTs"],
        },
    },
    {
        "name": "slack_search_public_and_private",
        "description": "Search across all accessible Slack channels (public and private).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "count": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "slack_send_message",
        "description": "Post a message to a Slack channel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelId": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["channelId", "text"],
        },
    },
    {
        "name": "slack_search_channels",
        "description": "Find Slack channels whose names contain a given substring.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Substring to match against channel names.",
                },
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["query"],
        },
    },
    {
        "name": "slack_get_user_profile",
        "description": "Get a Slack user's profile (display name, email, etc.).",
        "input_schema": {
            "type": "object",
            "properties": {"userId": {"type": "string"}},
            "required": ["userId"],
        },
    },
    # ------------------------------------------------------------------
    # Notion
    # ------------------------------------------------------------------
    {
        "name": "notion_fetch",
        "description": (
            "Fetch a Notion page or database by URL, page ID, or collection:// URI. "
            "Returns the page/database object including its properties."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Notion URL, page ID, database ID, or collection://uuid.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "notion_query_data_sources",
        "description": (
            "Query a Notion database. Accepts Notion API filter objects (not SQL). "
            "Example date filter: {\"property\": \"Date\", \"date\": {\"on_or_after\": \"2026-04-24\"}}. "
            "data_source_id may be a database ID or collection://uuid."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_source_id": {"type": "string"},
                "filter": {
                    "type": "object",
                    "description": "Notion API filter object.",
                },
                "sorts": {
                    "type": "array",
                    "description": "Array of Notion sort objects.",
                },
                "page_size": {"type": "integer", "default": 50},
            },
            "required": ["data_source_id"],
        },
    },
    {
        "name": "notion_query_meeting_notes",
        "description": (
            "Query a Notion meeting notes database. Same interface as "
            "notion_query_data_sources — accepts Notion API filter objects."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data_source_id": {"type": "string"},
                "filter": {"type": "object"},
                "sorts": {"type": "array"},
                "page_size": {"type": "integer", "default": 50},
            },
            "required": ["data_source_id"],
        },
    },
    {
        "name": "notion_search",
        "description": "Full-text search across Notion workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "filter_type": {
                    "type": "string",
                    "enum": ["page", "database"],
                    "description": "Limit results to pages or databases.",
                },
                "page_size": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "notion_create_pages",
        "description": "Create a new page inside a Notion database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "parent_id": {
                    "type": "string",
                    "description": "Database ID to create the page in.",
                },
                "properties": {
                    "type": "object",
                    "description": "Notion property values in API format.",
                },
                "children": {
                    "type": "array",
                    "description": "Optional page content blocks.",
                },
            },
            "required": ["parent_id", "properties"],
        },
    },
    {
        "name": "notion_update_page",
        "description": "Update properties on an existing Notion page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageId": {"type": "string"},
                "properties": {
                    "type": "object",
                    "description": "Notion property values in API format.",
                },
            },
            "required": ["pageId", "properties"],
        },
    },
    {
        "name": "notion_get_comments",
        "description": "Get comments on a Notion block or page.",
        "input_schema": {
            "type": "object",
            "properties": {"blockId": {"type": "string"}},
            "required": ["blockId"],
        },
    },
    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    {
        "name": "write_risk_register",
        "description": (
            "Persist the updated risk register to disk. "
            "Call this once at the end of the crawl with the complete updated JSON object. "
            "This is the only way the register is saved between runs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Complete risk register JSON (last_run, risks, suggested_dependencies).",
                }
            },
            "required": ["data"],
        },
    },
]
