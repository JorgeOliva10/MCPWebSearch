"""Security validation utilities."""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from config import MAX_QUERY_LENGTH


class SecurityValidator:
    """Validates input to prevent injection attacks."""

    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*$',
        r'expression\s*$',
    ]

    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """Sanitize search query to prevent injection."""
        if not query or not isinstance(query, str):
            raise ValueError("Invalid query")

        # Remove control characters except newline, carriage return, tab
        query = ''.join(char for char in query if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length using constant from config
        query = query[:MAX_QUERY_LENGTH]
        
        # Remove HTML tags
        query = BeautifulSoup(query, 'html.parser').get_text()

        return query.strip()

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and sanitize URL."""
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL")
        
        url = url.strip()
        
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL must include scheme (http/https) and domain")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only http and https schemes are allowed")
        
        return url