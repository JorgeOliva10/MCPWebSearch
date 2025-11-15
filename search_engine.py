"""Search engine implementation."""

import asyncio
import logging
import hashlib
from typing import Dict, List, Optional
from urllib.parse import quote_plus, quote
from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from config import SEARCH_ENGINES, REQUEST_TIMEOUT, USER_AGENT, MAX_CONCURRENT_SEARCHES
from cache import SearchCache
from security import SecurityValidator
from parsers import SearchParsers

logger = logging.getLogger(__name__)


class SearchEngine:
    """Handles search operations across multiple engines."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = SearchCache(max_size=200)
        self.security = SecurityValidator()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_SEARCHES)
        self.parsers = SearchParsers()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT, connect=5)
            connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_SEARCHES, limit_per_host=2)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={'User-Agent': USER_AGENT}
            )
        return self.session

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def _generate_cache_key(self, engine: str, query: str) -> str:
        """Generate cache key."""
        key_data = f"{engine}:{query}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def search_parallel(self, query: str, engines: List[str], max_results: int) -> tuple:
        """Execute parallel searches across multiple engines."""
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Starting parallel search across {len(engines)} engines")
        search_tasks = []
        for eng in engines:
            search_tasks.append(self._search_engine_with_cache(eng, query, max_results, timestamp))
        
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        all_results = []
        successful_engines = []
        failed_engines = []

        for eng, result in zip(engines, search_results):
            if isinstance(result, Exception):
                logger.error(f"Search failed for {eng}: {result}")
                failed_engines.append(eng)
            elif result:
                all_results.extend(result)
                successful_engines.append(eng)
                logger.info(f"Retrieved {len(result)} results from {eng}")

        return all_results, successful_engines, failed_engines, timestamp

    async def _search_engine_with_cache(self, engine: str, query: str, max_results: int, timestamp: str) -> List[Dict[str, str]]:
        """Search an engine with cache support and rate limiting."""
        async with self.semaphore:
            cache_key = self._generate_cache_key(engine, query)
            cached = self.cache.get(cache_key)

            if cached:
                results, _ = cached
                logger.info(f"Results from cache: {engine}")
                return results[:max_results]
            else:
                results = await self._search_engine(engine, query)
                self.cache.set(cache_key, (results, timestamp))
                return results[:max_results]

    async def _search_engine(self, engine: str, query: str) -> List[Dict[str, str]]:
        """Execute search on a specific engine."""
        search_url = SEARCH_ENGINES[engine].format(query=quote_plus(query))

        try:
            session = await self._get_session()
            async with session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"Search failed on {engine}: HTTP {response.status}")
                    return []

                html = await response.text()

            # Handle special parsers
            if engine == "brave":
                results = await asyncio.to_thread(self.parsers.parse_brave, html)
            else:
                results = self.parsers.parse_search_results(html, engine)

            # Add engine identifier to each result
            for result in results:
                result['engine'] = engine

            return results

        except Exception as e:
            logger.error(f"Error searching {engine}: {e}")
            return []

    def clear_cache(self):
        """Clear the search cache."""
        self.cache.clear()