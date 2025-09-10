from __future__ import annotations

from core.interfaces import AbstractMedia
# from core.repositories.manga import MangaChaptersRepository
from .manga_chapter import MangaChapter


class Manga(AbstractMedia[MangaChapter]):
    id_dex: str = ""
    artist: str = ""
