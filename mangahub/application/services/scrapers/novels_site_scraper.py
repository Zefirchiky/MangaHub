import asyncio
from typing import TYPE_CHECKING

import aiohttp
from domain.models.novels import Novel
from domain.models.sites import Site
from services.parsers import UrlParser

if TYPE_CHECKING:
    from controllers import SitesManager


class NovelsSiteScraper:
    is_done = False

    def __init__(self, sites_manager: "SitesManager"):
        self.manager = sites_manager

    async def get_title_page(self, site: Site, novel: Novel):
        url = UrlParser.get_title_page_url(site, novel)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers={"User-Agent": "Mozilla/5.0"}
            ) as response:
                return await response.text()

    async def get_chapter_page(self, url):
        url = url
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers={"User-Agent": "Mozilla/5.0"}
            ) as response:
                return await response.text()

    def start_get_chapter_page(self, url, callback):
        return asyncio.create_task(
            self._execute_function_and_notify(self.get_chapter_page, callback, url)
        )

    async def _execute_function_and_notify(self, fn1, fn2, *args, **kwargs):
        result = await fn1(*args, **kwargs)
        fn2(result)

    @staticmethod
    def get_temp_novel_text():
        with open("example_novel_chapter.txt", "r") as f:
            return f.read()
