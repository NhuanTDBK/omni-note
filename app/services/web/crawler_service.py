from typing import Tuple
import random
import httpx

from app.services.web.base_crawler import CrawlerService


class AsyncRequestCrawlerService(CrawlerService):
    def __init__(self):
        # Cache structure: {url: {'content': content, 'timestamp': timestamp, 'title': title}}
        super().__init__()
        # Cache expiration time in seconds (10 minutes)

        # List of common user agents to rotate through
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        ]
        # self.driver = get_driver_headless()
        self.web_client = httpx.AsyncClient()

    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(self.user_agents)

    async def fetch_url(self, url: str) -> Tuple[str, str]:
        """Fetch URL content"""
        # self.driver.get(url)
        # await asyncio.sleep(0.4)
        # return self.driver.title, self.driver.page_source
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers={"User-Agent": self._get_random_user_agent()}
            )
            response.raise_for_status()
            return "", response.text
