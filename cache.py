"""LRU cache implementation for search results."""

from typing import Dict, List, Optional

class SearchCache:
    """LRU cache for search results."""

    def __init__(self, max_size: int = 200):
        self.cache: Dict[str, tuple] = {}
        self.max_size = max_size
        self.access_order: List[str] = []

    def get(self, key: str) -> Optional[tuple]:
        """Get cached value and update access order."""
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: tuple):
        """Set cached value with LRU eviction."""
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = value
        self.access_order.append(key)

    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.access_order.clear()