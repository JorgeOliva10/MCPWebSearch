#!/usr/bin/env python3
"""Main entry point for MCP Search Server."""

import asyncio
import json
import sys
import logging

from models import MCPMessage
from server import MCPSearchServer

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main loop - reads JSON-RPC messages from stdin."""
    server = MCPSearchServer()

    try:
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    message_dict = json.loads(line)
                    message = MCPMessage.from_dict(message_dict)
                except json.JSONDecodeError as exc:
                    logger.error(f"Invalid JSON: {exc}")
                    continue

                response = await server.handle_message(message)

                if response:
                    print(json.dumps(response.to_dict()), flush=True)

            except (EOFError, KeyboardInterrupt):
                break
            except Exception as exc:
                logger.error(f"Unexpected error: {exc}", exc_info=True)

    finally:
        await server.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server terminated")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        sys.exit(1)