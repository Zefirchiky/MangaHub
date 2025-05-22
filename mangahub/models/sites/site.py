from __future__ import annotations
from pydantic import field_validator

from ..tags.tag_model import TagModel
from ..url import URL
from ..manga.manga import Manga
from .parsing_methods import MangaParsing, NovelParsing, MangaChapterParsing


class Site(TagModel):
    name: str
    url: str | URL
    manga_parsing: MangaParsing | None = None
    manga_chapter_parsing: MangaChapterParsing | None = None
    novel_parsing: NovelParsing | None = None
    
    num_identifier: str = ""
    language: str = "en"
    manga: dict[str, dict[str, str]] = {}

    @field_validator("url")
    def validate_url(cls, url: str | URL) -> URL:
        if isinstance(url, str):
            url = URL(url=url)
        return url

    def add_manga(self, manga: Manga, num_identifier: str = "") -> None:
        self.manga[manga.name] = {"id": manga.id_}
        if num_identifier:
            self.manga[manga.name]["num_identifier"] = num_identifier
        self.manga = self.manga
        return self.manga

    def remove_manga(self, manga_name: Manga | str) -> None:
        if isinstance(manga_name, Manga):
            manga_name = manga_name.name
        self.manga.pop(manga_name)
        return self.manga

    def get_manga_identifier(self, manga_name: str) -> str:
        return self.manga.get(manga_name, {}).get("num_identifier")
