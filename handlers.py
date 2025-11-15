"""Tool request handlers."""

import logging
from typing import Any, Dict
from urllib.parse import quote_plus

from models import MCPMessage, MCPError, ContentBlock, ToolResult
from config import SEARCH_ENGINES, SOCIAL_SEARCH, WEB_ARCHIVES_SEARCH, DEFAULT_RESULTS_PER_ENGINE
from search_engine import SearchEngine
from archive_service import ArchiveService
from tools import get_tool_definitions

logger = logging.getLogger(__name__)


class ToolHandlers:
    """Handles all tool requests."""

    def __init__(self, search_engine: SearchEngine, archive_service: ArchiveService):
        self.search_engine = search_engine
        self.archive_service = archive_service

    def handle_initialize(self, message: MCPMessage) -> MCPMessage:
        """Respond to initialization request."""
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "mcp-search-server",
                "version": "2.3.0"
            },
        }
        return MCPMessage(id=message.id, result=result)

    def handle_tools_list(self, message: MCPMessage) -> MCPMessage:
        """Return list of supported tools."""
        tools = get_tool_definitions()
        result = {"tools": [tool.to_dict() for tool in tools]}
        return MCPMessage(id=message.id, result=result)

    async def handle_web_search(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """Execute web search with parallel queries."""
        try:
            query = arguments.get("query")
            engine = arguments.get("engine", "all")
            max_results = min(arguments.get("max_results", DEFAULT_RESULTS_PER_ENGINE), 50)

            if not query:
                return self._create_error_response(
                    message_id, -32602, "Required parameter missing: query"
                )

            try:
                query = self.search_engine.security.sanitize_search_query(query)
            except ValueError as e:
                return self._create_error_response(
                    message_id, -32602, f"Invalid query: {str(e)}"
                )

            if engine == "all":
                engines_to_search = list(SEARCH_ENGINES.keys())
            elif engine in SEARCH_ENGINES:
                engines_to_search = [engine]
            else:
                return self._create_error_response(
                    message_id, -32602, f"Unsupported search engine: {engine}"
                )

            all_results, successful_engines, failed_engines, timestamp = \
                await self.search_engine.search_parallel(query, engines_to_search, max_results)

            output = self._format_search_results(query, all_results, successful_engines, 
                                                 failed_engines, engines_to_search, timestamp)

            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())

        except Exception as e:
            logger.error(f"Web search error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Search error: {str(e)}"
            )

    def _format_search_results(self, query: str, all_results: list, successful_engines: list,
                               failed_engines: list, engines_to_search: list, timestamp: str) -> str:
        """Format search results for output."""
        if not all_results:
            output = f"No results found for: {query}\n\n"
            if failed_engines:
                output += f"**Failed Engines**: {', '.join(failed_engines)}\n"
            return output

        output = f"# Search Results for '{query}'\n\n"
        output += f"**Engines Used**: {', '.join(successful_engines)} ({len(successful_engines)}/{len(engines_to_search)} successful)\n"
        if failed_engines:
            output += f"**Failed Engines**: {', '.join(failed_engines)}\n"
        output += f"**Total Results**: {len(all_results)}\n"
        output += f"**Timestamp**: {timestamp}\n\n"

        results_by_engine = {}
        for result in all_results:
            eng = result.get('engine', 'unknown')
            if eng not in results_by_engine:
                results_by_engine[eng] = []
            results_by_engine[eng].append(result)

        for eng in successful_engines:
            if eng in results_by_engine:
                output += f"## Results from {eng.title()} ({len(results_by_engine[eng])} results)\n\n"
                for i, result in enumerate(results_by_engine[eng], 1):
                    output += f"### {i}. {result['title']}\n"
                    output += f"**URL**: {result['url']}\n"
                    if result.get('snippet'):
                        output += f"**Snippet**: {result['snippet']}\n"
                    output += "\n"

        return output

    async def handle_social_search(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """Execute social media search."""
        try:
            query = arguments.get("query")
            platform = arguments.get("platform", "all")

            if not query:
                return self._create_error_response(
                    message_id, -32602, "Required parameter missing: query"
                )

            try:
                query = self.search_engine.security.sanitize_search_query(query)
            except ValueError as e:
                return self._create_error_response(
                    message_id, -32602, f"Invalid query: {str(e)}"
                )

            if platform == "all":
                platforms = list(SOCIAL_SEARCH.keys())
            elif platform in SOCIAL_SEARCH:
                platforms = [platform]
            else:
                return self._create_error_response(
                    message_id, -32602, f"Unsupported platform: {platform}"
                )

            output = f"# Social Search: '{query}'\n\n"
            output += f"**Platforms ({len(platforms)})**: {', '.join(platforms)}\n\n"
            
            for plat in platforms:
                search_url = SOCIAL_SEARCH[plat].format(query=quote_plus(query))
                output += f"**{plat}**: {search_url}\n"

            output += "\n*Note: Direct URLs for browser use. Automated scraping may require authentication.*\n"

            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())

        except Exception as e:
            logger.error(f"Social search error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Search error: {str(e)}"
            )

    async def handle_archives_search(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """Search for archived versions of a URL."""
        try:
            url = arguments.get("url")
            service = arguments.get("service", "all")
            check_availability = arguments.get("check_availability", False)

            if not url:
                return self._create_error_response(
                    message_id, -32602, "Required parameter missing: url"
                )

            try:
                url = self.search_engine.security.validate_url(url)
            except ValueError as e:
                return self._create_error_response(
                    message_id, -32602, f"Invalid URL: {str(e)}"
                )

            if service == "all":
                services = list(WEB_ARCHIVES_SEARCH.keys())
            elif service in WEB_ARCHIVES_SEARCH:
                services = [service]
            else:
                return self._create_error_response(
                    message_id, -32602, f"Unsupported archives service: {service}"
                )

            wayback_data = None
            if check_availability and ('wayback' in services or service == 'all'):
                wayback_data = await self.archive_service.check_wayback_availability(url)

            output = self.archive_service.generate_archive_urls(url, services, wayback_data)

            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())

        except Exception as e:
            logger.error(f"Archives search error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Archives search error: {str(e)}"
            )

    async def handle_list_engines(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """List all available search engines."""
        try:
            output = f"# Available Privacy-Focused Search Engines ({len(SEARCH_ENGINES)} total)\n\n"
            output += "**Default Behavior**: Searches ALL engines in parallel\n\n"
            
            categories = {
                "Popular Privacy Engines": ['duckduckgo', 'brave', 'startpage', 'ecosia'],
                "Independent Engines": ['mojeek'],
                "International": ['yandex']
            }
            
            for category, engines in categories.items():
                output += f"## {category}\n"
                for engine in engines:
                    if engine in SEARCH_ENGINES:
                        output += f"- **{engine}**: `{SEARCH_ENGINES[engine]}`\n"
                output += "\n"
            
            output += "## Usage\n"
            output += "- By default, `web_search` searches ALL engines in parallel\n"
            output += "- Use `engine` parameter to search a specific engine\n"
            output += "- When using 'all', returns up to 20 results from each engine\n"
            output += "- Parallel execution significantly speeds up multi-engine searches\n"

            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())

        except Exception as e:
            logger.error(f"List engines error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Error listing engines: {str(e)}"
            )

    async def handle_list_archives_services(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """List all available archive services."""
        try:
            output = f"# Available Archives Services ({len(WEB_ARCHIVES_SEARCH)} total)\n\n"
            output += "These services store archived versions of web pages.\n\n"
            
            categories = {
                "Long-term Archives": ['wayback', 'archive_today', 'ghostarchive'],
                "Search Engine Caches": ['google_cache', 'bing_cache', 'yandex_cache'],
                "Aggregators": ['cachedview']
            }
            
            for category, services_list in categories.items():
                output += f"## {category}\n\n"
                for svc in services_list:
                    if svc in WEB_ARCHIVES_SEARCH:
                        info = WEB_ARCHIVES_SEARCH[svc]
                        output += f"### {info['name']}\n"
                        output += f"{info['description']}\n"
                        output += f"**Service ID**: `{svc}`\n\n"
            
            output += "## Key Features by Service\n\n"
            output += "**Wayback Machine (wayback)**: 800+ billion pages archived since 1996\n"
            output += "**archive.today**: On-demand archiving with permanent snapshots\n"
            output += "**Google Cache**: Temporary cache updated regularly\n"
            output += "**CachedView**: Meta-search across multiple archives\n"
            output += "**GhostArchive**: Specialized in social media and video content\n"

            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())

        except Exception as e:
            logger.error(f"List archives error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Error listing archives: {str(e)}"
            )

    async def handle_clear_cache(self, message_id: Any, arguments: Dict[str, Any]) -> MCPMessage:
        """Clear the search cache."""
        try:
            self.search_engine.clear_cache()
            output = "✅ Search cache cleared successfully"
            result = ToolResult([ContentBlock("text", output)])
            return MCPMessage(id=message_id, result=result.to_dict())
        except Exception as e:
            logger.error(f"Cache clear error: {e}", exc_info=True)
            return self._create_error_response(
                message_id, -32603, f"Clear error: {str(e)}"
            )

    @staticmethod
    def _create_error_response(message_id: Any, code: int, message: str) -> MCPMessage:
        """Create a JSON-RPC error response."""
        return MCPMessage(id=message_id, error=MCPError(code, message).to_dict())