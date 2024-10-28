from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .base_model import BaseModel
from .manga_chapter import MangaChapter
from .site import Site
from .tags.tag import Tag


@dataclass
class Manga(BaseModel):
    name: str
    _id: str
    cover: str
    description: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    status: str = "Unknown"
    year: Optional[int] = None
    _id_dex: str = ''
    last_updated: datetime = field(default_factory=datetime.now)
    sites: List[Site] = field(default_factory=list)
    chapters: Dict[int, MangaChapter] = field(default_factory=dict)
    tags: List[Tag] = field(default_factory=list)
    
    def add_site(self, site: Site) -> None:
        if site not in self.sites:
            self.sites.append(site)
            
    def add_chapter(self, chapter: MangaChapter) -> None:
        self.chapters[chapter.number] = chapter
        self.last_updated = datetime.now()
        
    def get_chapter(self, number: int) -> Optional[MangaChapter]:
        return self.chapters.get(number)
        
    def add_tag(self, tag: Tag) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
