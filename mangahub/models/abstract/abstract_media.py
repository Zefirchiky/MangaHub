from abc import ABC
from datetime import datetime
from pydantic import Field, PrivateAttr
from ..tags.tag_model import TagModel
from .abstract_chapter import AbstractChapter


class AbstractMedia(ABC, TagModel):
    name: str
    id_: str
    description: str = ''
    author: str = ''
    status: str = "Unknown"
    
    folder: str = ''
    cover: str = ''
    
    year: int = 0
    last_updated: str = Field(default_factory=lambda: str(datetime.now))
    
    site: str = 'MangaDex'
    backup_sites: set[str] = set()
    
    current_chapter: int | float = 0
    last_chapter: int | float = 0
    checked_chapters: set[int | float] = set()
    _chapters_data: dict[int | float, AbstractChapter] = PrivateAttr(default_factory=dict)
        
    def add_backup_site(self, site_name) -> None:
        self.backup_sites.add(site_name)
                
    def add_chapter(self, chapter: AbstractChapter) -> None:
        if chapter.number not in self._chapters_data.keys():
            self._chapters_data[chapter.number] = chapter
            self.update()
            
    def check_chapter(self, chapter_num: int | float) -> None:
        self.checked_chapters.add(chapter_num)
        
    def uncheck_chapter(self, chapter_num: int | float) -> None:
        self.checked_chapters.remove(chapter_num)
    
    def update(self) -> None:
        self.last_updated = str(datetime.now())