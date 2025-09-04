from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QPixmap
from services.downloaders import ImageDownloader
from core.models.images import ImageMetadata, ImageCache
from core.models.manga import MangaChapter
from utils.placeholder_generator import PlaceholderGenerator
from config import Config


class ChapterImageLoader(QObject):
    placeholder_ready = Signal(
        str, int, int, QPixmap
    )  # manga id, chapter num, placement index, placeholder
    image_ready = Signal(
        str, int, int, str, bytes
    )  # manga id, chapter num, placement index, image filename, image

    def __init__(self, image_downloader: ImageDownloader, cache: ImageCache):
        super().__init__()
        self.downloader = image_downloader
        self.cache = cache

        self.downloader.metadata_downloaded.connect(self._metadata_downloaded)
        self.downloader.image_downloaded.connect(self._image_downloaded)
        self.overall_download_progress = self.downloader.overall_download_progress
        self.finished = self.downloader.finished
        self.finished.connect(self._set_chapter_total_bytes)

        self.manga_id: str = ""
        self.chapter: MangaChapter = None
        self.urls = {}
        self.urls_num = {}

        self._emited_metadata = set()

    @Slot(int)  # type: ignore
    def _set_chapter_total_bytes(self, total: int):
        self.chapter.total_bytes = total

    def load_chapter(self, manga_id: str, chapter: MangaChapter):
        self._reset()
        self.manga_id = manga_id
        self.chapter = chapter

        for num, img in chapter._images.get_all().items():
            self.urls[img.metadata.url] = img.name
            self.urls_num[img.metadata.url] = num

        self.downloader.download_images(
            self.urls,
            convert=Config.Downloading.Image.convert_image(),
            total_bytes=chapter.total_bytes,
        )

    def _metadata_downloaded(self, url: str, metadata: ImageMetadata):
        if url not in self._emited_metadata:
            placeholder = PlaceholderGenerator.static(
                metadata.width,
                metadata.height,
                f"{self.urls[url]} (#{self.urls_num[url]})",
            )

            self._emited_metadata.add(url)
            self.placeholder_ready.emit(
                self.manga_id, self.chapter.num, self.urls_num[url], placeholder
            )
            self.chapter._images.get(self.urls_num[url]).metadata = metadata

    def _image_downloaded(self, url: str, name: str, metadata: ImageMetadata):
        self.chapter._images.get(self.urls_num[url]).metadata.name = name
        self.image_ready.emit(
            self.manga_id,
            self.chapter.num,
            self.urls_num.pop(url),
            name,
            self.cache.get(name),
        )
        if not self.urls_num:
            self.finished.emit(1)

    def _reset(self):
        self.urls = {}
        self.urls_num = {}
        self._emited_metadata = set()
