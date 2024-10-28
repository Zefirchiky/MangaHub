from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from .base_model import BaseModel


@dataclass
class MangaChapter(BaseModel):
    number: int
    name: str
    upload_date: datetime = field(default_factory=datetime.now)
    _id_dex: str = ''
    images: Dict[int, str] = field(default_factory=dict)
    translator: Optional[str] = None
    language: str = 'en'
    
    def add_image(self, num: int, image: str) -> None:
        self.images[num] = image
    
    def add_images(self, images: Dict[int, str]) -> None:
        self.images.update(images)
        
    def get_image(self, num: int) -> Optional[str]:
        return self.images.get(num)
