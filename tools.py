"""Tool definitions for MCP Search Server."""

from typing import List
from models import Tool
from config import SEARCH_ENGINES, SOCIAL_SEARCH, WEB_ARCHIVES_SEARCH, MAX_QUERY_LENGTH


def get_tool_definitions() -> List[Tool]:
    """Return list of all supported tools."""
    return [
        Tool(
            name="web_search",
            description=f"Search the web using {len(SEARCH_ENGINES)} privacy-focused search engines in parallel. By default searches ALL engines simultaneously and returns up to 20 results from each. Returns titles, snippets, and URLs.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"Search query (max {MAX_QUERY_LENGTH} characters)"
                    },
                    "engine": {
                        "type": "string",
                        "enum": list(SEARCH_ENGINES.keys()) + ["all"],
                        "description": "Search engine to use, or 'all' to search across all engines in parallel",
                        "default": "all"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results per engine (1-50). When using 'all', this applies to each engine individually",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 50
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="social_search",
            description="Search across popular social media platforms (Twitter, Reddit, YouTube, GitHub, StackOverflow, Medium, Pinterest, TikTok, Instagram, Facebook, LinkedIn) in parallel. Public content only.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"Search query (max {MAX_QUERY_LENGTH} characters)"
                    },
                    "platform": {
                        "type": "string",
                        "enum": list(SOCIAL_SEARCH.keys()) + ["all"],
                        "description": "Social platform to search, or 'all' for all platforms in parallel",
                        "default": "all"
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="archives_search",
            description=f"Search for archived versions of a URL across {len(WEB_ARCHIVES_SEARCH)} web archive (Wayback Machine, archive.today, Google Cache, Bing Cache, Yandex Cache, CachedView, GhostArchive). Useful for accessing removed content or viewing historical versions.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Complete URL to search in archives (must include http:// or https://)"
                    },
                    "service": {
                        "type": "string",
                        "enum": list(WEB_ARCHIVES_SEARCH.keys()) + ["all"],
                        "description": "Archives service to use, or 'all' to check all services",
                        "default": "all"
                    },
                    "check_availability": {
                        "type": "boolean",
                        "description": "For Wayback Machine, check API to verify if archives exist",
                        "default": False
                    }
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="list_engines",
            description="List all available search engines with their details.",
            input_schema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_archives_services",
            description="List all available archives services with their details.",
            input_schema={"type": "object", "properties": {}},
        ),
        Tool(
            name="clear_cache",
            description="Clear the search results cache.",
            input_schema={"type": "object", "properties": {}},
        ),
    ]