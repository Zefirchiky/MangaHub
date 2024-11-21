from pydantic import Field, PrivateAttr
from datetime import datetime
from .manga_chapter import MangaChapter
from .tags.tag_model import TagModel


class Manga(TagModel):
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
    
    current_chapter: int | float = 0
    last_chapter: int | float = 0
    checked_chapters: set[int | float] = set()
    _chapters_data: dict[int | float, MangaChapter] = PrivateAttr(default_factory=dict)
    
    def add_backup_site(self, site_name) -> None:
        self.backup_sites.add(site_name)
            
    def add_chapter(self, chapter: MangaChapter) -> None:
        if chapter.number not in self._chapters_data.keys():
            self._chapters_data[chapter.number] = chapter
            self.update()
            
    def check_chapter(self, chapter_num) -> None:
        self.checked_chapters.add(chapter_num)
        
    def uncheck_chapter(self, chapter_num) -> None:
        self.checked_chapters.remove(chapter_num)
        
    def update(self) -> None:
        self.last_updated = str(datetime.now())