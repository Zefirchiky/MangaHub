from __future__ import annotations
import time
from itertools import batched
from PySide6.QtCore import Signal, QObject
from loguru import logger

from core.models.abstract import AbstractMedia
from core.models.manga import Manga, MangaChapter
from core.models.images import ImageCache, ImageMetadata
from models import Url
from .image_downloader import ImageDownloadManager
from .html_downloader import HtmlDownloader
from config import Config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class DownloadManager(QObject):
    image_downloaded = Signal(str, float, int, ImageMetadata) # manga id, chapter num, image num, name
    image_metadata_downloaded = Signal(str, float, int, ImageMetadata)   # manga id, chapter num, image num, metadata
    # overall_image_download_progress = ImageDownloader.overall_download_progress  # len(urls), percent, current bytes, total bytes
    # image_download_progress = ImageDownloadManager.download_progress
    image_download_error = ImageDownloadManager.download_error
    images_downloaded = ImageDownloadManager.all_downloaded
    
    html_downloaded = HtmlDownloader.signals.downloaded   # url, content
    all_html_downloaded = Signal()
    cover_downloaded = Signal(str, bytes)   # manga_id, image
    
    manga_details_downloaded = Signal(str)
    
    def __init__(self, app: App):
        super().__init__()
        self.images_cache = app.images_cache
        self.image_downloader = ImageDownloadManager(self.images_cache)
        self.html_downloader = HtmlDownloader()
        
        self.sites_manager = app.sites_manager
        self.chapter_images_urls_downloaded = self.sites_manager.manga_chapter_signals.image_urls   # manga id, chapter num, image
        
        self.image_downloader.metadata_downloaded.connect(self._image_metadata_downloaded)
        self.image_downloader.downloaded.connect(self._image_downloaded)
        self.image_downloader.all_downloaded.connect(lambda: print('IT WORKS: ', time.perf_counter() - self.dt))
        
        self.queue: dict[str, dict[str, list[Url]]] = {}
        self._cover_downloads: dict[str, str] = {}
        self._image_urls: dict[str, tuple[str, float, int]] = {}
        self.dt = 0
    
    def _url_from_url(self, url: str | Url) -> str:
        return url if isinstance(url, str) else url.url
    
    def download_cover(self, media: AbstractMedia):
        if isinstance(media, Manga):
            if media.cover:
                self._download_cover(media.id_, media.cover)
            else:
                self.sites_manager.download_manga_cover(media)  # TODO: It should just be generalized
        
    def _download_cover(self, media_id: str, url: str):
        if not media_id:
            logger.error('DownloadManager.download_cover did not received manga_id')
            return
        if not url:
            logger.error('DownloadManager.download_cover did not received url')
            return
        self.image_downloader.download_images_sep_thread(url, f'cover_{media_id}')
        self._cover_downloads[url] = media_id
        
    def download_manga_chapter_details(self, manga: Manga, chapter: MangaChapter):
        self.sites_manager.download_manga_chapter_details(manga, chapter)
        
    def download_manga_chapter_images(self, manga_id: str, chapter: MangaChapter):
        all_urls = [image.metadata.url for image in chapter.get_data_repo().get_all().values()]
        
        for num, image in chapter.get_data_repo().get_all().items():
            self._image_urls[image.metadata.url] = (manga_id, chapter.num, num)
            
        urls_names = [(url, f'chap-image_{manga_id}_{str(chapter.num).replace('.', '-')}_{i}') for i, url in enumerate(all_urls)]
        self.dt = time.perf_counter()
        for batch in list(batched(urls_names, 3)):
            urls, names = [], []
            for url, name in batch:
                urls.append(url)
                names.append(name)
            self.image_downloader.download_images_sep_thread(urls, names)
        
    def download_html(self, name: str, url: str | Url):
        url = self._url_from_url(url)
        if not self.queue.get(name):
            self.queue[name] = {}
        if not self.queue[name].get('html'):
            self.queue[name]['html'] = []
        if url not in self.queue[name]['html']:
            self.queue[name]['html'].append(url)
        
    def download_htmls(self, urls: list[str | Url]):
        for i, url in enumerate(urls):
            urls[i] = self._url_from_url(url)
        return self.html_downloader.download_htmls(urls)
    
    def _image_metadata_downloaded(self, metadata: ImageMetadata):
        manga_id, chapter_num, num = self._image_urls.get(metadata.url)
        self.image_metadata_downloaded.emit(manga_id, chapter_num, num, metadata)
    
    def _image_downloaded(self, metadata: ImageMetadata):
        if metadata.name.startswith('cover'):
            self.cover_downloaded.emit(self._cover_downloads.pop(metadata.url), self.images_cache.pop(metadata.name))
        elif metadata.name.startswith('chap-image'):
            manga_id, chapter_num, num = self._image_urls.pop(metadata.url)
            self.image_downloaded.emit(manga_id, chapter_num, num, metadata)
        else:
            logger.warning(f'Unknown image was downloaded: {metadata.url} ({metadata.name}, {metadata})')
    
    def start(self, name: str):
        if content := self.queue.pop(name, None):
            for type_, urls in content.items():
                match type_:
                    case 'html':
                        self.html_downloader.download_htmls(urls)
                    case 'img':
                        self.image_downloader.download_images_sep_thread(urls)