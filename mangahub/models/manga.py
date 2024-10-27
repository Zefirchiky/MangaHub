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
    
    def set_id_dex(self, id_dex: str) -> None:
        self._id_dex = id_dex

    def add_site(self, site) -> None:
        self.sites.append(site.name)

    def add_chapter(self, chapter: MangaChapter) -> None:
        self.chapters.append(chapter)