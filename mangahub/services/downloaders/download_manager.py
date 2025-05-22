from PySide6.QtCore import Signal, QObject
from loguru import logger

from models.images import ImageCache
from models import URL
from .image_downloader import ImageDownloader
from .html_downloader import HtmlDownloader
from config import Config


class DownloadManager(QObject):
    image_downloaded = ImageDownloader.image_downloaded # url, name.ext, metadata
    image_metadata_downloaded = ImageDownloader.metadata_downloaded   # url, metadata
    overall_image_download_progress = ImageDownloader.overall_download_progress  # len(urls), percent, current bytes, total bytes
    image_download_progress = ImageDownloader.download_progress
    image_download_error = ImageDownloader.download_error
    images_downloaded = ImageDownloader.finished
    
    html_downloaded = HtmlDownloader.signals.downloaded   # url, content
    all_html_downloaded = Signal()
    cover_downloaded = Signal(str, bytes)   # manga_name, image
    
    def __init__(self):
        super().__init__()
        self.images_cache = ImageCache(Config.Dirs.IMAGES_CACHE, Config.Caching.Image.max_ram(), Config.Caching.Image.max_disc())
        self.image_downloader = ImageDownloader(self.images_cache)
        self.html_downloader = HtmlDownloader()
        
        self.image_downloader.image_downloaded.connect(self._image_downloaded)
        
        self.queue: dict[str, dict[str, list[URL]]] = {}
        self._cover_downloads: dict[str, str] = {}
        
    def _init_connections(self):
        self.html_downloaded.connect(self._on_html_downloaded)
    
    def _url_from_url(self, url: str | URL) -> str:
        return url if isinstance(url, str) else url.url
    
    def download_cover(self, manga_name: str, url: str):
        if not manga_name:
            logger.error('DownloadManager.download_cover did not received manga_name')
            return
        if not url:
            logger.error('DownloadManager.download_cover did not received url')
            return
        self.image_downloader.download_image(url, f'cover-{url}')
        self._cover_downloads[url] = manga_name
    
    def download_image(self, url: str | URL, name=''):
        if not name:
            name = self._url_from_url(url)
        self.image_downloader.download_image(url, name)
        
    def download_images(self, urls: dict[str | URL, str]):
        for url, name in urls.items():
            if not name:
                urls[url] = self._url_from_url(url)
        self.image_downloader.download_images(urls)
        
    def download_images_metadata(self, urls: list[str | URL]):
        for i, url in enumerate(urls):
            urls[i] = self._url_from_url(url)
        self.image_downloader.download_metadatas(urls)
        
    def download_html(self, name: str, url: str | URL):
        url = self._url_from_url(url)
        if not self.queue.get(name):
            self.queue[name] = {}
        if not self.queue[name].get('html'):
            self.queue[name]['html'] = []
        if url not in self.queue[name]['html']:
            self.queue[name]['html'].append(url)
        
    def download_htmls(self, urls: list[str | URL]):
        for i, url in enumerate(urls):
            urls[i] = self._url_from_url(url)
        return self.html_downloader.download_htmls(urls)
    
    def _image_downloaded(self, url: str, name: str, metadata: str):
        if name.startswith('cover'):
            self.cover_downloaded.emit(self._cover_downloads.pop(url), self.images_cache.pop(name))
    
    def start(self, name: str):
        if content := self.queue.pop(name, None):
            for type_, urls in content:
                match type_:
                    case 'html':
                        self.html_downloader.download_htmls(urls)
                    case 'img':
                        self.image_downloader.download_images(urls)