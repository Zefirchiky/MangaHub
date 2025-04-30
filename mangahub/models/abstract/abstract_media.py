from __future__ import annotations

from abc import ABC
from datetime import datetime

from pydantic import Field, PrivateAttr

from ..tags.tag_model import TagModel
from .abstract_chapter import AbstractChapter, ChapterNotFoundError


class AbstractMedia[ChapterType: AbstractChapter](ABC, TagModel):
    name: str
    id_: str
    description: str = ""
    author: str = ""
    status: str = "Unknown"

    folder: str = ""
    cover: str = ""

    year: int = 0
    last_updated: str = Field(default_factory=lambda: str(datetime.now))

    site: str = "MangaDex"
    backup_sites: list[str] = []

    current_chapter: int | float = 0
    last_read_chapter: int | float = 0
    first_chapter: int | float = 0
    last_chapter: int | float = 0
    checked_chapters: set[int | float] = Field(default_factory=set)
    _chapters_data: dict[int | float, ChapterType] = PrivateAttr(default_factory=dict)

    def add_backup_site(self, site_name) -> None:
        self.backup_sites.add(site_name)

    def add_chapter(self, chapter: ChapterType) -> AbstractMedia:
        if chapter.number not in self._chapters_data.keys():
            self._chapters_data[chapter.number] = chapter
            self.update()
        return self

    def get_all_sites(self):
        sites = self.backup_sites.copy()
        sites.insert(0, self.site)
        return sites

    def get_chapter(self, chapter_num: int | float, default_return=None) -> ChapterType:
        if chapter := self._chapters_data.get(chapter_num):
            return chapter
        return default_return

    def check_chapter(self, chapter_num: int | float) -> None:
        if chapter_num > self.last_read_chapter:
            self.last_read_chapter = chapter_num
        self.checked_chapters.add(chapter_num)

    def uncheck_chapter(self, chapter_num: int | float) -> None:
        self.checked_chapters.remove(chapter_num)

    def update(self) -> None:
        self.last_updated = str(datetime.now())

    def __str__(self) -> str:
        return f"Manga {self.name} ({self.id_})"
