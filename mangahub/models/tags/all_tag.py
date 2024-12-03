from ..manga.manga import Manga
from ..manga.manga_chapter import MangaChapter
from .tag import Tag
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AllTag(Tag):
    belonging: Dict[str, str] = field(default_factory=dict)
    
    def add_manga(self, manga: Manga):
        self.belonging[manga] = manga.name

    def add_chapter(self, chapter: MangaChapter):
        self.belonging[chapter] = chapter.name

    # def add_chapter_image(self, chapter_image: MangaChapterImage):
    #     self.belonging[chapter_image] = chapter_image.number