from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime
from .manga_chapter import MangaChapter
from .tags.tag_model import TagModel


class Manga(TagModel, BaseModel):
    name: str
    id_: str
    id_dex: str = ''
    
    folder: str = ''
    cover: str = ''
    
    description: str = ''
    author: str = ''
    artist: str = ''
    status: str = "Unknown"
    year: int = 0
    last_updated: str = Field(default_factory=lambda: str(datetime.now))
    
    site: str = 'MangaDex'
    backup_sites: set[str] = set()
    
    current_chapter: int = 0
    last_chapter: int = 0
    chapters: set[float] = set()
    _chapters_data: dict[float, MangaChapter] = PrivateAttr(default_factory=dict)
    
    def add_backup_site(self, site_name) -> None:
        self.backup_sites.add(site_name)
            
    def add_chapter(self, chapter: MangaChapter) -> None:
        if chapter.number not in self._chapters_data.keys():
            self._chapters_data[chapter.number] = chapter
            self.update()
            
    def check_chapter(self, chapter_num) -> None:
        self.chapters.add(chapter_num)
        
    def uncheck_chapter(self, chapter_num) -> None:
        self.chapters.remove(chapter_num)
        
    def update(self) -> None:
        self.last_updated = str(datetime.now())