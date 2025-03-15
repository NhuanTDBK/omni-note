from typing import Tuple
import random
import asyncio

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


class AsyncRequestCrawlerService:
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
        self.web_client = get_driver_headless()

    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(self.user_agents)

    async def fetch_url(self, url: str) -> Tuple[str, str]:
        """Fetch URL content"""
        self.web_client.get(url)
        await asyncio.sleep(0.4)
        return self.web_client.title, self.web_client.page_source

    def stop(self):
        self.web_client.quit()
