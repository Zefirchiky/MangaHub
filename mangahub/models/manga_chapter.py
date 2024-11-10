from pydantic import BaseModel, Field
from .tags.tag_model import TagModel
from .chapter_image import ChapterImage


class MangaChapter(TagModel, BaseModel):
    number: float
    name: str = ''
    id_dex: str = ''
    url: str = ''
    upload_date: str = ''
    translator: str = ''
    language: str = 'en'
    _images: dict[int, ChapterImage] = {}
    
    def add_image(self, num: int, image: str) -> None:
        self._images[num] = image
    
    def add_images(self, images: dict[int, str]) -> None:
        self._images.update(images)
        
    def get_image(self, num: int) -> str:
        return self._images.get(num)
