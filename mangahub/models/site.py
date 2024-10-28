from dataclasses import dataclass, field
from typing import Dict, Optional
from .base_model import BaseModel

@dataclass
class Site(BaseModel):
    name: str
    url: str
    language: str = 'en'
    title_page: Dict[str, str] = field(default_factory=dict)
    chapter_page: Dict[str, str] = field(default_factory=dict)
    manga: Dict[str, Dict[str, str]] = field(default_factory=dict)
    rate_limit: Optional[float] = None
    
    def add_manga(self, manga_name: str, num_identifier: Optional[str] = None) -> None:
        self.manga[manga_name] = {
            'name': manga_name,
            'num_identifier': num_identifier
        }
        
    def get_manga_identifier(self, manga_name: str) -> Optional[str]:
        return self.manga.get(manga_name, {}).get('num_identifier')
