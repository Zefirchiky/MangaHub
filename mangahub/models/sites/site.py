from __future__ import annotations
from pydantic import field_validator

from ..tags.tag_model import TagModel
from ..url import URL
from .parsing_methods import MangaParsing, NovelParsing, MangaChapterParsing


class Site(TagModel):
    name: str
    url: str | URL
    manga_parsing: MangaParsing | None = None
    manga_chapter_parsing: MangaChapterParsing | None = None
    novel_parsing: NovelParsing | None = None
    
    num_identifier: str = ""
    language: str = "en"
    manga: list[str] = []

    @field_validator("url")
    def validate_url(cls, url: str | URL) -> URL:
        if isinstance(url, str):
            url = URL(url=url)
        return url

    def add_manga(self, manga_id: str) -> None:
        self.manga.append(manga_id)
        self.manga = self.manga
        return self.manga

    def remove_manga(self, manga_id: str) -> None:
        self.manga.pop(manga_id)
        return self.manga
