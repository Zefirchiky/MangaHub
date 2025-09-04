from __future__ import annotations

from abc import ABC
from datetime import datetime
from pathlib import Path

from pydantic import Field, PrivateAttr

from ..tags.tag_model import TagModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .abstract_chapter import AbstractChapter
    from core.repositories.abstract import ChaptersRepository


class AbstractMedia[ChapterType: AbstractChapter](ABC, TagModel):
    name: str
    id_: str
    folder: Path
    description: str = ""
    author: str = ""
    status: str = "Unknown"

    cover: str = ""

    year: int = 0
    last_updated: str = Field(default_factory=lambda: str(datetime.now))

    sites: list[str] = ["MangaDex"]

    current_chapter: float = -1
    last_read_chapter: float = -1
    checked_chapters: set[float] = Field(default_factory=set)
    
    _chapters_repo: ChaptersRepository[ChapterType] = PrivateAttr(default=None)

    def add_site(self, site_name: str, index=-1) -> None:
        self._changed = True
        self.sites.insert(index, site_name)

    def add_chapter(self, chapter: ChapterType) -> AbstractMedia:
        self._changed = True
        self._chapters_repo.add(chapter.num, chapter)
        return self

    def get_all_sites(self) -> list[str]:
        sites = self.sites.copy()
        return sites

    def get_chapter(self, chapter_num: float, default_return=None) -> ChapterType:
        if chapter_num <= 0 or ((chap := self._chapters_repo.get_i(-1, None)) and chapter_num >= chap.num):
            return default_return
        if chapter := self._chapters_repo.get(chapter_num):
            return chapter
        return default_return

    def check_chapter(self, chapter_num: float) -> None:
        self._changed = True
        if chapter_num > self.last_read_chapter:
            self.last_read_chapter = chapter_num
        self.checked_chapters.add(chapter_num)

    def uncheck_chapter(self, chapter_num: float) -> None:
        self._changed = True
        self.checked_chapters.remove(chapter_num)

    def __str__(self) -> str:
        return f"Manga {self.name} ({self.id_})"
