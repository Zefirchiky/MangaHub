from .chapter_image import ChapterImage
from ..abstract.abstract_chapter import AbstractChapter


class MangaChapter(AbstractChapter):
    id_dex: str = ''
    url: str = ''
    urls_cached: bool = False
    total_bytes: int = 0
    _images: dict[int, ChapterImage] = {}