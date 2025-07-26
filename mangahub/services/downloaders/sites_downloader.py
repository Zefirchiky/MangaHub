from enum import Enum, auto
import asyncio
from PySide6.QtCore import QObject, Signal
import httpx
from loguru import logger

from services.downloaders.html_downloader import HtmlDownloaderWorker
from ..parsers import UrlParser
from .html_downloader import HtmlDownloader
from utils.pyside_threading import ThreadingManager
from config import Config


class SiteUrlTypes(Enum):
    TITLE_PAGE = auto()
    CHAPTER_PAGE = auto()

class SitesDownloader(QObject):
    downloader = HtmlDownloader()
    
    title_page_downloaded = Signal(str, str)
    title_page_downloading_error = Signal(str, str)
    chapter_page_downloaded = Signal(str, str)
    chapter_page_downloading_error = Signal(str, str)
    
    url_checked = Signal(str, int)
    all_urls_checked = Signal()
    
    def __init__(self):
        super().__init__()
        self.url_parser = UrlParser()
        
        self.downloader.signals.downloaded.connect(self._downloaded)
        self.downloader.error.connect(self._downloading_error)
        self.downloader.signals.all_downloaded.connect(self._all_downloaded)
        
        self._urls_downloading: dict[str, SiteUrlTypes] = {}
        self._retries: dict[str, int] = {}
        
        self._pending_tasks = []
        self._client = None
        
        logger.success("SitesDownloader initialized")
        
    def _downloaded(self, url: str, content: str):
        if url not in self._urls_downloading:
            logger.warning(f'Unknown url was downloaded: {url}')
            return None
        
        type_ = self._urls_downloading.pop(url)
        logger.success(f'Url `{url} ({type_})` was successfully downloaded')
        match type_:
            case SiteUrlTypes.TITLE_PAGE:
                self.title_page_downloaded.emit(url, content)
            case SiteUrlTypes.CHAPTER_PAGE:
                self.chapter_page_downloaded.emit(url, content)
                    
    def _downloading_error(self, url: str, error: str):
        if url not in self._urls_downloading:
            logger.warning(f'Unknown url failed to download: {url}')
            return None
        
        if not self._retries.get(url):
            self._retries[url] = 1
        else:
            self._retries[url] += 1
            if self._retries[url] >= Config.Downloading.max_retries():
                type_ = self._urls_downloading.pop(url)
                logger.error(f'Failed to download `{url}` (type: {type_}) after {self._retries[url]} retries')
                match type_:
                    case SiteUrlTypes.TITLE_PAGE:
                        self.title_page_downloading_error.emit(url, error)
                    case SiteUrlTypes.CHAPTER_PAGE:
                        self.chapter_page_downloading_error.emit(url, error)
                        
            else:
                self.downloader.download_html(url)
                    
    def _all_downloaded(self):
        if self._urls_downloading:  # If not all urls are downloaded, but downloader is finished
            logger.warning(f'Not all urls were downloaded, remaining: {self._urls_downloading}')

    def download_title_page(self, url: str):
        if url in self._urls_downloading:
            return self.downloader.workers[url]
        self._urls_downloading[url] = SiteUrlTypes.TITLE_PAGE
        return self.downloader.download_html(url)

    def download_chapter_page(self, url: str) -> HtmlDownloaderWorker:
        if url in self._urls_downloading:
            return self.downloader.workers[url]
        self._urls_downloading[url] = SiteUrlTypes.CHAPTER_PAGE
        return self.downloader.download_html(url)

    def check_urls(self, urls: list[str]):
        self._pending_tasks = []
        ThreadingManager.run(self._check_urls, urls)
        
    def _check_urls(self, urls: list[str]):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(loop.create_task(self._check_urls_async(urls)))
        loop.close()
        
    async def _check_urls_async(self, urls):
        async with httpx.AsyncClient(timeout=10) as client:
            for url in urls:
                cr = self._check_url_async(url, client)
                task = asyncio.create_task(cr)
                self._pending_tasks.append(task)
                
            await self._wait_for_all_tasks()
        
    async def _wait_for_all_tasks(self):
        if self._pending_tasks:
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
        self.all_urls_checked.emit()
        self._pending_tasks = []
            
    async def _check_url_async(self, url: str, client: httpx.AsyncClient):
        asyncio.current_task().set_name(f"check_url_task_{url}")
        try:
            response = await client.head(url, follow_redirects=True)
            self.url_checked.emit(url, response.status_code)
        except httpx.RequestError as e:
            logger.error(f"HTTPX request error for {url}: {e}")
            self.url_checked.emit(url, -1) # Emit an error status code or handle as appropriate
        except Exception as e:
            logger.error(f"An unexpected error occurred for {url}: {e}")
            self.url_checked.emit(url, -2) # Emit a different error status code