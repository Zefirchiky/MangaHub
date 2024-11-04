from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .base_model import BaseModel
from .manga_chapter import MangaChapter
from .tags.tag import Tag


@dataclass
class Manga(BaseModel):
    name: str
    _id: str
    _id_dex: str = ''
    cover: str = ''
    current_chapter: Optional[int] = None
    last_chapter: Optional[int] = None
    description: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    status: str = "Unknown"
    year: Optional[int] = None
    last_updated: str = str(datetime.now())
    sites: List[str] = field(default_factory=list)
    chapters: Dict[int, MangaChapter] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)
    
    def add_site(self, site) -> None:
        if site not in self.sites:
            self.sites.append(site)
            
    def add_chapter(self, chapter: MangaChapter) -> None:
        if chapter.number not in self.chapters:
            self.chapters[chapter.number] = chapter
            self.last_updated = str(datetime.now())
        
    def add_tag(self, tag: Tag) -> None:
        if tag not in self.tags:
            self.tags.append(tag)