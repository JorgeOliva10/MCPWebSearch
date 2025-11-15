"""Web archive service implementation."""

import logging
from typing import Dict, Any, Optional
from urllib.parse import quote

import aiohttp

from config import WEB_ARCHIVES_SEARCH, REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


class ArchiveService:
    """Handles web archive operations."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT, connect=5)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'User-Agent': USER_AGENT}
            )
        return self.session

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def check_wayback_availability(self, url: str) -> Optional[Dict[str, Any]]:
        """Check Wayback Machine API for archive availability."""
        try:
            api_url = f"https://archive.org/wayback/available?url={quote(url, safe='')}"
            session = await self._get_session()
            
            async with session.get(api_url) as response:
                if response.status != 200:
                    logger.warning(f"Wayback API returned status {response.status}")
                    return None
                
                data = await response.json()
                
                if data.get('archived_snapshots') and data['archived_snapshots'].get('closest'):
                    snapshot = data['archived_snapshots']['closest']
                    
                    # Get additional stats if available
                    stats_url = f"https://web.archive.org/__wb/sparkline?url={quote(url, safe='')}&collection=web&output=json"
                    try:
                        async with session.get(stats_url) as stats_response:
                            if stats_response.status == 200:
                                stats = await stats_response.json()
                                total_snapshots = sum(stats.get('years', {}).values()) if 'years' in stats else 0
                                first_ts = stats.get('first_ts', 'Unknown')
                                last_ts = stats.get('last_ts', 'Unknown')
                            else:
                                total_snapshots = 1
                                first_ts = snapshot.get('timestamp', 'Unknown')
                                last_ts = snapshot.get('timestamp', 'Unknown')
                    except:
                        total_snapshots = 1
                        first_ts = snapshot.get('timestamp', 'Unknown')
                        last_ts = snapshot.get('timestamp', 'Unknown')
                    
                    return {
                        'available': True,
                        'snapshots': total_snapshots,
                        'first_timestamp': self._format_wayback_timestamp(first_ts),
                        'latest_timestamp': self._format_wayback_timestamp(last_ts),
                        'latest_url': snapshot.get('url', ''),
                        'status': snapshot.get('status', '')
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error checking Wayback availability: {e}")
            return None

    @staticmethod
    def _format_wayback_timestamp(timestamp: str) -> str:
        """Format Wayback Machine timestamp to readable date."""
        try:
            if timestamp == 'Unknown' or not timestamp:
                return 'Unknown'
            
            # Wayback timestamps are in format: YYYYMMDDhhmmss
            if len(timestamp) >= 8:
                year = timestamp[0:4]
                month = timestamp[4:6]
                day = timestamp[6:8]
                
                if len(timestamp) >= 14:
                    hour = timestamp[8:10]
                    minute = timestamp[10:12]
                    second = timestamp[12:14]
                    return f"{year}-{month}-{day} {hour}:{minute}:{second} UTC"
                else:
                    return f"{year}-{month}-{day}"
            
            return timestamp
        except:
            return str(timestamp)

    def generate_archive_urls(self, url: str, services: list, wayback_data: Optional[Dict] = None) -> str:
        """Generate formatted output with archive URLs."""
        output = f"# Archives Versions of URL\n\n"
        output += f"**Original URL**: {url}\n"
        output += f"**Services Checked ({len(services)})**: {', '.join(services)}\n\n"

        # Wayback status
        if wayback_data:
            output += f"**Wayback Machine Status**: ✅ {wayback_data['snapshots']} snapshots available\n"
            output += f"**First Snapshot**: {wayback_data['first_timestamp']}\n"
            output += f"**Latest Snapshot**: {wayback_data['latest_timestamp']}\n"
            output += f"**Latest URL**: {wayback_data['latest_url']}\n\n"
        elif 'wayback' in services:
            output += "**Wayback Machine Status**: ❌ No snapshots found\n\n"

        # Generate archive URLs
        output += "## Available web archive\n\n"
        
        for svc in services:
            service_info = WEB_ARCHIVES_SEARCH[svc]
            output += f"### {service_info['name']}\n"
            output += f"**Description**: {service_info['description']}\n"
            
            if svc == 'wayback':
                output += f"**Browse All Snapshots**: {service_info['search_url'].format(url=quote(url, safe=''))}\n"
                if wayback_data and wayback_data.get('latest_url'):
                    output += f"**Latest Snapshot**: {wayback_data['latest_url']}\n"
                output += f"**API Check**: {service_info['api_url'].format(url=quote(url, safe=''))}\n"
            
            elif svc == 'archive_today':
                output += f"**Search Archives**: {service_info['search_url'].format(url=quote(url, safe=''))}\n"
                output += f"**Create New Archive**: {service_info['save_url'].format(url=quote(url, safe=''))}\n"
            
            else:
                output += f"**Access Cache**: {service_info['search_url'].format(url=quote(url, safe=''))}\n"
            
            output += "\n"

        output += "## Usage Tips\n\n"
        output += "- **Wayback Machine**: Best for comprehensive historical archives (1996-present)\n"
        output += "- **archive.today**: Creates permanent, immutable snapshots on demand\n"
        output += "- **Google/Bing Cache**: Temporary caches, updated frequently but may disappear\n"
        output += "- **CachedView**: Aggregator that searches multiple sources automatically\n"
        output += "- **GhostArchive**: Specialized for social media and video content\n"
        output += "\n*Note: Archives availability varies by service and content age. Some services may require CAPTCHA verification.*\n"

        return output