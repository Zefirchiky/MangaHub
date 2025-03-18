from __future__ import annotations

from pydantic import PrivateAttr

from ..abstract.abstract_media import AbstractMedia
from .manga_chapter import MangaChapter


class Manga(AbstractMedia):
    id_dex: str = ''
    artist: str = ''
    _chapters_data: dict[int | float, MangaChapter] = PrivateAttr(default_factory=dict)

    def add_chapter(self, chapter: MangaChapter) -> Manga:
        super().add_chapter(chapter)
        return self