import time
from typing import Tuple
import random
import httpx

import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver_headless():
    chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless=new")  # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    driver = webdriver.Chrome(options=chrome_options)
    return driver


class WebProcessor:
    def __init__(self):
        # Cache structure: {url: {'content': content, 'timestamp': timestamp, 'title': title}}
        self.cache = {}
        # Cache expiration time in seconds (10 minutes)
        self.cache_expiry = 600
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
