from __future__ import annotations
from core.interfaces import AbstractChapter
from .chapter_image import ChapterImage


class MangaChapter(AbstractChapter[int, ChapterImage]):
    id_dex: str = ""
    url: str = ""
    urls_cached: bool = False
    total_bytes: int = 0