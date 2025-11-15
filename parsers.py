"""HTML parsing utilities for different search engines."""

import logging
from typing import Dict, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SearchParsers:
    """Collection of parsers for different search engines."""

    @staticmethod
    def parse_brave(html: str) -> List[Dict[str, str]]:
        """Parse Brave search results."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        containers = soup.find_all("div", class_=lambda c: c and "snippet" in c.lower())
        for div in containers:
            anchor = div.find("a", href=True)
            if not anchor:
                continue

            title_elem = div.find(["h1", "h2", "h3"])
            if not title_elem:
                title_elem = anchor

            title = title_elem.get_text(strip=True)

            snippet = ""
            para = div.find("p")
            if para:
                snippet = para.get_text(strip=True)

            results.append({
                "title": title,
                "url": anchor["href"],
                "snippet": snippet
            })

        return results

    @staticmethod
    def parse_duckduckgo(soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Parse DuckDuckGo search results."""
        results = []
        
        for result in soup.find_all('div', class_='result'):
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')

            if title_elem:
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'url': title_elem.get('href', ''),
                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ""
                })
        
        return results

    @staticmethod
    def parse_mojeek(soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Parse Mojeek search results."""
        results = []
        
        for result in soup.find_all(['div', 'article'],
                                    class_=lambda x: x and ('result' in x.lower())):
            title_elem = result.find(['h3', 'a'])
            link_elem = result.find('a', href=True)
            snippet_elem = result.find(['p', 'span'],
                                      class_=lambda x: x and ('desc' in x.lower() or 'snippet' in x.lower()))

            if title_elem and link_elem:
                url = link_elem.get('href', '')
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'url': url,
                    'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ""
                })
        
        return results

    @staticmethod
    def parse_generic(soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Generic parser for unknown search engines."""
        results = []
        
        for link in soup.find_all('a', href=True):
            parent = link.parent
            if parent and parent.name in ['div', 'article', 'li']:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if title and len(title) > 10 and url.startswith('http'):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': ""
                    })
                    
                if len(results) >= 20:
                    break
        
        return results

    @classmethod
    def parse_search_results(cls, html: str, engine: str) -> List[Dict[str, str]]:
        """Parse search results based on engine type."""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        try:
            if engine == "duckduckgo":
                results = cls.parse_duckduckgo(soup)
            elif engine == "mojeek":
                results = cls.parse_mojeek(soup)
            else:
                results = cls.parse_generic(soup)

        except Exception as e:
            logger.error(f"Error parsing {engine} results: {e}")

        return results