from .manga_chapter import MangaChapter
from .site import Site
from dataclasses import dataclass, field
from typing import List


@dataclass
class Manga:
    name: str
    _id: str
    cover: str
    _id_dex: str = ''
    sites: List[Site] = field(default_factory=list)
    chapters: List[MangaChapter] = field(default_factory=list)

    def add_site(self, site):
        self.sites.append(site.name)

    def add_chapter(self, chapter: MangaChapter) -> None:
        self.chapters.append(chapter)