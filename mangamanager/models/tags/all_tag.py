from ..manga import Manga
from ..manga_chapter import MangaChapter
from ..manga_chapter_image import MangaChapterImage
from .tag import Tag
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AllTag(Tag):
    belonging: Dict['manga': Manga.name, 
                    'chapters': MangaChapter.name,
                    'chapter_images': MangaChapterImage.number] = field(default_factory=dict)
    
    def add_manga(self, manga: Manga):
        self.belonging[manga] = manga.name

    def add_chapter(self, chapter: MangaChapterImage):
        self.belonging[chapter] = chapter.name

    def add_chapter_image(self, chapter_image: MangaChapterImage):
        self.belonging[chapter_image] = chapter_image.number