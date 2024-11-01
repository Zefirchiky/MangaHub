from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from .base_model import BaseModel
from .chapter_image import ChapterImage


@dataclass
class MangaChapter(BaseModel):
    number: int
    name: str = ''
    _id_dex: str = ''
    url: str = ''
    upload_date: str = ''
    translator: Optional[str] = None
    language: str = 'en'
    images: Dict[int, ChapterImage] = field(default_factory=dict)
    
    def add_image(self, num: int, image: str) -> None:
        self.images[num] = image
    
    def add_images(self, images: Dict[int, str]) -> None:
        self.images.update(images)
        
    def get_image(self, num: int) -> Optional[str]:
        return self.images.get(num)
