from .chapter_image import ChapterImage
from ..abstract.abstract_chapter import AbstractChapter


class MangaChapter(AbstractChapter):
    id_dex: str = ''
    url: str = ''
    _images: dict[int, ChapterImage] = {}