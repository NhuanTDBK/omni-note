import time
from typing import Tuple

import trafilatura


class CrawlerService:
    def __init__(self):
        self.cache = {}
        self.cache_expiry = 600

    async def extract_content(self, url: str) -> Tuple[str, str]:
        """
        Fetch content from URL, using cache if available and not expired

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (title, main_content)
        """
        current_time = time.time()

        # Check if URL is in cache and not expired
        if url in self.cache:
            cache_entry = self.cache[url]
            if current_time - cache_entry["timestamp"] < self.cache_expiry:
                return cache_entry["title"], cache_entry["content"]

        try:
            data = await self.fetch_url(url)
            title, content = data

            content = trafilatura.extract(
                filecontent=content,
                output_format="markdown",
                include_tables=True,
            )

            # Cache the result
            self.cache[url] = {
                "content": content,
                "title": title,
                "timestamp": current_time,
            }

            return title, content

        except Exception as e:
            return f"Error fetching URL: {url}", f"An error occurred: {str(e)}"

    def clear_cache(self) -> None:
        """Clear the URL cache"""
        self.cache.clear()

    @staticmethod
    def from_config(config):
        return CrawlerService()