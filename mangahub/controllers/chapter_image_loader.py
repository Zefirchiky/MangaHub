from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap
from services.downloaders import ImageDownloader
from models.images import ImageMetadata, ImageCache
from models.manga import MangaChapter
from .placeholder_generator import PlaceholderGenerator


class ChapterImageLoader(QObject):
    placeholder_ready = Signal(str, int, int, QPixmap)
    
    def __init__(self, image_downloader: ImageDownloader, cache: ImageCache):
        self.downloader = image_downloader
        self.cache = cache
        
        self.downloader.metadata_downloaded.connect(self._metadata_downloaded)
        self.downloader.image_downloaded.connect(self._image_downloaded)
        
        self.manga_id = None
        self.chapter = None
        self.urls = {}
        self.urls_num = {}
        
    def load_chapter(self, manga_id: str, chapter: MangaChapter):
        self.manga_id = manga_id
        self.chapter = chapter
        
        self.urls = {}
        for num, img in chapter._images.items():
            self.urls[img.metadata.url] = f'{manga_id}_{chapter.number}_{num}'
            self.urls_num[img.metadata.url] = num
            
        self.downloader.download_images(self.urls)
        
    def _metadata_downloaded(self, url: str, metadata: ImageMetadata):
        placeholder = PlaceholderGenerator.static(metadata.width, metadata.height, self.urls[url])
        
        self.placeholder_ready.emit(self.manga_id, self.chapter.number, self.urls_num[url], placeholder)
        
    def _image_downloaded(self): pass