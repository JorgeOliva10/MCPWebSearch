"""Configuration constants for MCP Search Server."""

# Request settings
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEFAULT_RESULTS_PER_ENGINE = 20
MAX_CONCURRENT_SEARCHES = 6

# Search query limits
MAX_QUERY_LENGTH = 500

# Search Engines
SEARCH_ENGINES = {
    'duckduckgo': 'https://html.duckduckgo.com/html/?q={query}',
    'brave':      'https://search.brave.com/search?q={query}',
    'ecosia':     'https://www.ecosia.org/search?q={query}',
    'startpage':  'https://www.startpage.com/do/search?q={query}',
    'mojeek':     'https://www.mojeek.com/search?q={query}',
    'yandex':     'https://yandex.com/search/?text={query}',
}

# Social Media Search Endpoints
SOCIAL_SEARCH = {
    'twitter':       'https://twitter.com/search?q={query}&src=typed_query',
    'reddit':        'https://www.reddit.com/search/?q={query}',
    'youtube':       'https://www.youtube.com/results?search_query={query}',
    'github':        'https://github.com/search?q={query}&type=repositories',
    'stackoverflow': 'https://stackoverflow.com/search?q={query}',
    'medium':        'https://medium.com/search?q={query}',
    'pinterest':     'https://www.pinterest.com/search/pins/?q={query}',
    'tiktok':        'https://www.tiktok.com/search?q={query}',
    'instagram':     'https://www.instagram.com/explore/tags/{query}/',
    'facebook':      'https://www.facebook.com/public/{query}',
    'linkedin':      'https://www.linkedin.com/search/results/all/?keywords={query}',
}

# Web Archive Services
WEB_ARCHIVES_SEARCH = {
    'wayback': {
        'name': 'Wayback Machine (Internet Archive)',
        'search_url': 'https://web.archive.org/web/*/{url}',
        'api_url': 'https://archive.org/wayback/available?url={url}',
        'direct_url': 'https://web.archive.org/web/{timestamp}/{url}',
        'description': 'Archivio storico completo con snapshot multipli dal 1996'
    },
    'archive_today': {
        'name': 'archive.today / archive.ph',
        'search_url': 'https://archive.ph/{url}',
        'save_url': 'https://archive.ph/?run=1&url={url}',
        'description': 'Archivio permanente e immutabile, utile per preservare prove'
    },
    'google_cache': {
        'name': 'Google Cache',
        'search_url': 'https://webcache.googleusercontent.com/search?q=cache:{url}',
        'description': 'Cache temporanea di Google (può essere rimossa)'
    },
    'bing_cache': {
        'name': 'Bing Cache',
        'search_url': 'https://www.bing.com/search?q=url:{url}',
        'description': 'Cache di Bing (accesso via ricerca)'
    },
    'yandex_cache': {
        'name': 'Yandex Cache',
        'search_url': 'https://yandex.com/search/?text=url:{url}',
        'description': 'Cache del motore russo Yandex'
    },
    'cachedview': {
        'name': 'CachedView',
        'search_url': 'https://cachedview.com/search?url={url}',
        'description': 'Aggregatore che cerca in Google, Wayback e Archive.today'
    },
    'ghostarchive': {
        'name': 'GhostArchive',
        'search_url': 'https://ghostarchive.org/search?term={url}',
        'description': 'Archivio specializzato in contenuti video e social media'
    }
}