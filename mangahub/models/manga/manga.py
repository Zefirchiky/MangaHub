from __future__ import annotations

from pydantic import PrivateAttr

from ..abstract.abstract_media import AbstractMedia
from .manga_chapter import MangaChapter


class Manga(AbstractMedia[MangaChapter]):
    id_dex: str = ""
    artist: str = ""
    _chapters_data: dict[int | float, MangaChapter] = PrivateAttr(default_factory=dict)
