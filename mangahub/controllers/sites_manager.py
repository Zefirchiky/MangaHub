from __future__ import annotations
from enum import Enum, auto
from PySide6.QtCore import QObject, Signal
from loguru import logger
from models import URL
from models.manga import Manga, MangaChapter
from models.sites import Site
from models.sites.parsing_methods import MangaParsing, NameParsing, CoverParsing, ChaptersListParsing, MangaChapterParsing, ImagesParsing
from services.repositories import SitesRepository
from services.downloaders import SitesDownloader
from services.parsers import UrlParser
from config import Config


class DownloadTypes(Enum):
    MANGA = auto()
    MANGA_CHAPTER = auto()

class MangaSignals(QObject):    # manga name, content
    name = Signal(str, str)
    cover_url_downloaded = Signal(str, str)
    chapters_list = Signal(str, list)
    
class MangaChapterSignals(QObject): # manga name, chapter num, content
    name = Signal(str, int, str)
    image_urls = Signal(str, int, list[str])
    

class SitesManager:
    repo = SitesRepository(Config.Dirs.SITES_JSON)
    downloader = SitesDownloader()
    url_parser = UrlParser()
    
    manga_signals = MangaSignals()
    manga_chapter_signals = MangaChapterSignals()
    
    def __init__(self):
        self.downloader.downloader.signals.downloaded.connect(self._url_downloaded)
        
        self._manga_downloading: dict[str, tuple[str, Site, Manga, DownloadTypes]] = {}
        self._manga_chapter_downloading: dict[str, tuple[str, Site, Manga, MangaChapter, DownloadTypes]] = {}
        
        logger.success("SitesManager initialized")

    def create_site(
        self,
        name: str,
        url: str,
        manga_parsing: MangaParsing,
        manga_chapter_parsing: MangaChapterParsing,
        **kwargs,
    ) -> Site:
        site = Site(
            name=name,
            url=url,
            manga_parsing=manga_parsing,
            manga_chapter_parsing=manga_chapter_parsing,
            **kwargs,
        ).set_changed()
        self.repo.add(name, site)
        return site

    def get_all(self) -> dict[str, Site]:
        return self.repo.get_all()

    def get(self, name: str = None, url: str | URL = None) -> Site | None:
        if url:
            url = URL(url)
            for site in self.repo.get_all().values():
                if site["url"] == url.site_url:
                    return site
        return self.repo.get(name)
    
    def _url_downloaded(self, url: str, content: str):
        if url in self._manga_downloading:
            path, site, manga, download_type = self._manga_downloading.get(url)
        elif url in self._manga_chapter_downloading:
            path, site, manga, chapter, download_type = self._manga_chapter_downloading.get(url)
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
                            self.manga_signals.name.emit(manga.name, result)
                        case DownloadTypes.MANGA_CHAPTER:
                            self.manga_chapter_signals.name.emit(manga.name, chapter.num, result)
                elif isinstance(parsing, CoverParsing):
                    self.manga_signals.cover_url_downloaded.emit(manga.name, result[0])
                elif isinstance(parsing, ChaptersListParsing):
                    self.manga_signals.chapters_list.emit(manga.name, result[0])
                elif isinstance(parsing, ImagesParsing):
                    self.manga_chapter_signals.image_urls.emit(manga.name, chapter.num, result)
    
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
    
    def download_manga_chapter_image_urls(self, manga: Manga, num: int):
        self.downloader.download_chapter_page(self.get(manga.sites[0]), manga, num)

    def save(self):
        self.repo.save()
