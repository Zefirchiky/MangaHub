from __future__ import annotations
from enum import Enum, auto
from PySide6.QtCore import QObject, Signal
import httpx
import asyncio
from loguru import logger

from models import Url
from core.models.abstract import AbstractMedia
from core.models.manga import Manga, MangaChapter
from core.models.sites_ import SiteModel
from core.models.sites_.parsing_methods import MangaParsing, NameParsing, CoverParsing, ChaptersListParsing, MangaChapterParsing, ImagesParsing
from services.repositories import SitesRepository
from services.downloaders import SitesDownloader
from services.parsers import UrlParser
from config import Config


class DownloadTypes(Enum):
    MANGA = auto()
    MANGA_CHAPTER = auto()

class MangaSignals(QObject):    # manga id, content
    name = Signal(str, str)
    cover_url_downloaded = Signal(str, str)
    chapters_list = Signal(str, list)
    sites_checked = Signal(str, list)
    
class MangaChapterSignals(QObject): # manga id, chapter num, content
    name = Signal(str, float, str)
    image_urls = Signal(str, float, list)
    

class SitesManager:
    repo = SitesRepository(Config.Dirs.DATA.SITES_JSON)
    downloader = SitesDownloader()
    url_parser = UrlParser()
    
    manga_signals = MangaSignals()
    manga_chapter_signals = MangaChapterSignals()
    
    def __init__(self):
        self.downloader.downloader.signals.downloaded.connect(self._url_downloaded)
        self.downloader.url_checked.connect(self._url_checked)
        self.downloader.all_urls_checked.connect(lambda: self.manga_signals.sites_checked.emit(self._checking_media, self._checking_media_sites))
        
        self._manga_downloading: dict[str, tuple[str, SiteModel, Manga, DownloadTypes]] = {}
        self._manga_chapter_downloading: dict[str, tuple[str, SiteModel, Manga, float, DownloadTypes]] = {}
        
        self._checking_media = None
        self._checking_media_sites = []
        
        logger.success("SitesManager initialized")

    def create_site(
        self,
        name: str,
        url: str,
        manga_parsing: MangaParsing,
        manga_chapter_parsing: MangaChapterParsing,
        **kwargs,
    ) -> SiteModel:
        site = SiteModel(
            name=name,
            url=url,
            manga_parsing=manga_parsing,
            manga_chapter_parsing=manga_chapter_parsing,
            **kwargs,
        ).set_changed()
        self.repo.add(name, site)
        return site

    def get_all(self) -> dict[str, SiteModel]:
        return self.repo.get_all()

    def get(self, name: str = None, url: str | Url = None) -> SiteModel | None:
        if url:
            url = Url(url)
            for site in self.repo.get_all().values():
                if site["url"] == url.site_url:
                    return site
        return self.repo.get(name)
    
    def get_site_from_url(self, url: Url):
        for site in self.get_all().values():
            if url.url.startswith(site.url.url):
                return site

    def find_media_sites(self, media_id: str):
        urls = []
        for site in self.get_all().values():
            urls.append(f'{site.url}/series/{media_id}-ffffffff')
        self.downloader.check_urls(urls)
        self._checking_media = media_id

    def _url_checked(self, url: str, code: int):
        if code == 200:
            self._checking_media_sites.append(self.get_site_from_url(Url(url)).name)
    
    def _url_downloaded(self, url: str, content: str):
        if url in self._manga_downloading:
            path, site, manga, download_type = self._manga_downloading.get(url)
        elif url in self._manga_chapter_downloading:
            path, site, manga, chapter_num, download_type = self._manga_chapter_downloading.get(url)
        else:
            logger.warning(f'Unknown url was downloaded: {url}')
            return None
        
        if not content:
            logger.warning(f'Url {url} does not have a content')
            return
        
        for parsing in site.manga_parsing.get_parsing_methods():
            if parsing.path == path:
                result = parsing.parse_html(content)
                if not result:
                    logger.warning(f'Parsing {parsing.path} returned None')
                    return
                
                if isinstance(parsing, NameParsing):
                    match download_type:
                        case DownloadTypes.MANGA:
                            self.manga_signals.name.emit(manga.id_, result[0])
                        case DownloadTypes.MANGA_CHAPTER:
                            self.manga_chapter_signals.name.emit(manga.id_, chapter_num, result[0])
                elif isinstance(parsing, CoverParsing):
                    self.manga_signals.cover_url_downloaded.emit(manga.id_, result[0])
                elif isinstance(parsing, ChaptersListParsing):
                    self.manga_signals.chapters_list.emit(manga.id_, result[0])
                elif isinstance(parsing, ImagesParsing):
                    self.manga_chapter_signals.image_urls.emit(manga.id_, chapter_num, result[0])
                    
        for parsing in site.manga_chapter_parsing.get_parsing_methods():
            if parsing.path == path:
                result = parsing.parse_html(content)
                if not result:
                    logger.warning(f'Parsing {parsing.path} returned None')
                    return
                
                if isinstance(parsing, NameParsing):
                    match download_type:
                        case DownloadTypes.MANGA:
                            self.manga_signals.name.emit(manga.id_, result[0])
                        case DownloadTypes.MANGA_CHAPTER:
                            self.manga_chapter_signals.name.emit(manga.id_, chapter_num, result[0])
                elif isinstance(parsing, CoverParsing):
                    self.manga_signals.cover_url_downloaded.emit(manga.id_, result[0])
                elif isinstance(parsing, ChaptersListParsing):
                    self.manga_signals.chapters_list.emit(manga.id_, result[0])
                elif isinstance(parsing, ImagesParsing):
                    self.manga_chapter_signals.image_urls.emit(manga.id_, chapter_num, list(dict.fromkeys(result)))
    
    def download_manga_cover(self, manga: Manga):
        site = self.get(manga.sites[0])
        if not site:
            logger.warning(f'No site with name {manga.sites[0]}')
            return
        
        url = f'{site.url}/{UrlParser.fill_media_url(site.manga_parsing.cover_parsing.path, manga)}'
        self._manga_downloading[url] = (site.manga_parsing.cover_parsing.path, site, manga, DownloadTypes.MANGA)
        self.downloader.download_title_page(url)
    
    def download_manga_details(self, manga: Manga):
        site = self.get(manga.sites[0])
        to_parse = []
        for parsing in site.manga_parsing.get_parsing_methods():
            if parsing.path not in to_parse:
                to_parse.append(parsing.path)
        
        urls = []
        for path in to_parse:
            urls.append(UrlParser.fill_media_url(
                f'{site.url}/{path}', manga
            ))
        
        for url, path in zip(urls, to_parse):
            self._manga_downloading[url] = (path, site, manga, DownloadTypes.MANGA)
            self.downloader.download_title_page(url)   #TODO: different sites retry
    
    def download_manga_chapter_details(self, manga: Manga, num: int):
        site = self.get(manga.sites[0])
        to_parse = []
        for parsing in site.manga_chapter_parsing.get_parsing_methods():
            if parsing.path not in to_parse:
                to_parse.append(parsing.path)
        
        urls = []
        for path in to_parse:
            urls.append(UrlParser.fill_chapter_url(
                f'{site.url}/{path}', manga.id_, num
            ))
        
        for url, path in zip(urls, to_parse):
            self._manga_chapter_downloading[url] = (path, site, manga, num, DownloadTypes.MANGA_CHAPTER)
            self.downloader.download_chapter_page(url) #TODO: different sites retry

    def save(self):
        self.repo.save()
