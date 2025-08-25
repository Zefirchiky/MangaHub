from __future__ import annotations

from ..abstract.abstract_media import AbstractMedia
from .manga_chapter import MangaChapter


class Manga(AbstractMedia[MangaChapter]):
    id_dex: str = ""
    artist: str = ""
    sites: list[str] = ['MangaDex']
