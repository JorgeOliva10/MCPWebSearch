"""MCP Search Server core implementation."""

import logging
from typing import Optional

from models import MCPMessage
from search_engine import SearchEngine
from archive_service import ArchiveService
from handlers import ToolHandlers
from config import SEARCH_ENGINES, WEB_ARCHIVES_SEARCH

logger = logging.getLogger(__name__)


class MCPSearchServer:
    """MCP server for web search across multiple engines, social media, and web archive."""

    def __init__(self):
        self.search_engine = SearchEngine()
        self.archive_service = ArchiveService()
        self.handlers = ToolHandlers(self.search_engine, self.archive_service)

        logger.info("Search server initialized with %d search engines and %d web archive", 
                   len(SEARCH_ENGINES), len(WEB_ARCHIVES_SEARCH))

    async def close(self):
        """Close all services."""
        await self.search_engine.close()
        await self.archive_service.close()

    async def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """Handle incoming RPC messages."""
        try:
            if message.method == "initialize":
                return self.handlers.handle_initialize(message)
            elif message.method == "tools/list":
                return self.handlers.handle_tools_list(message)
            elif message.method == "tools/call":
                return await self._handle_tool_call(message)
            else:
                return self.handlers._create_error_response(
                    message.id, -32601, f"Method not found: {message.method}"
                )
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return self.handlers._create_error_response(
                message.id, -32603, f"Internal error: {str(e)}"
            )

    async def _handle_tool_call(self, message: MCPMessage) -> MCPMessage:
        """Handle a tool call."""
        try:
            params = message.params
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "web_search":
                return await self.handlers.handle_web_search(message.id, arguments)
            elif tool_name == "social_search":
                return await self.handlers.handle_social_search(message.id, arguments)
            elif tool_name == "archives_search":
                return await self.handlers.handle_archives_search(message.id, arguments)
            elif tool_name == "list_engines":
                return await self.handlers.handle_list_engines(message.id, arguments)
            elif tool_name == "list_archives_services":
                return await self.handlers.handle_list_archives_services(message.id, arguments)
            elif tool_name == "clear_cache":
                return await self.handlers.handle_clear_cache(message.id, arguments)
            else:
                return self.handlers._create_error_response(
                    message.id, -32602, f"Unknown tool: {tool_name}"
                )
        except Exception as e:
            logger.error(f"Error executing tool: {e}", exc_info=True)
            return self.handlers._create_error_response(
                message.id, -32603, f"Error executing tool: {str(e)}"
            )