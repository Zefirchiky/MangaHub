from pydantic import BaseModel, Field
from .tags.tag_model import TagModel
from .chapter_image import ChapterImage


class MangaChapter(TagModel, BaseModel):
    number: int
    name: str = ''
    id_dex: str = ''
    url: str = ''
    upload_date: str = ''
    translator: str = ''
    language: str = 'en'
    images: dict[int, ChapterImage] = {}
    
    def add_image(self, num: int, image: str) -> None:
        self.images[num] = image
    
    def add_images(self, images: dict[int, str]) -> None:
        self.images.update(images)
        
    def get_image(self, num: int) -> str:
        return self.images.get(num)
