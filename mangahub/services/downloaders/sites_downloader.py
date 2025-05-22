from enum import Enum, auto
from PySide6.QtCore import QObject, Signal
from loguru import logger

from services.downloaders.html_downloader import HtmlDownloaderWorker
from ..parsers import UrlParser
from models.sites import Site
from models.abstract import AbstractMedia
from .html_downloader import HtmlDownloader
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
    
    def __init__(self):
        super().__init__()
        self.url_parser = UrlParser()
        
        self.downloader.signals.downloaded.connect(self._downloaded)
        self.downloader.error.connect(self._downloading_error)
        self.downloader.signals.all_downloaded.connect(self._all_downloaded)
        
        self._urls_downloading: dict[str, SiteUrlTypes] = {}
        self._retries: dict[str, int] = {}
        
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
        self._urls_downloading[url] = SiteUrlTypes.TITLE_PAGE
        return self.downloader.download_html(url)

    def download_chapter_page(self, site: Site, media: AbstractMedia, num: int) -> HtmlDownloaderWorker:
        url = UrlParser.get_chapter_url(
            site.chapter_page.url_format, media.id_, num
        )
        self._urls_downloading[url] = SiteUrlTypes.CHAPTER_PAGE
        return self.downloader.download_html(url)
