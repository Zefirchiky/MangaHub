from ..tags.tag_model import TagModel
from .chapter_image import ChapterImage


class MangaChapter(TagModel):
    number: int | float
    name: str = ''
    id_dex: str = ''
    url: str = ''
    upload_date: str = ''
    translator: str = ''
    language: str = 'en'
    _images: dict[int, ChapterImage] = {}
    
    def add_image(self, image: ChapterImage) -> None:
        self._images[image.number] = image
    
    def add_images(self, images: list[ChapterImage]) -> None:
        for image in images:
            self.add_image(image)

