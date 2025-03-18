from .chapter_image import ChapterImage
from ..abstract.abstract_chapter import AbstractChapter


class MangaChapter(AbstractChapter):
    id_dex: str = ''
    url: str = ''
    _images: dict[int, ChapterImage] = {}
    
    def add_image(self, image: ChapterImage) -> None:
        self._images[image.number] = image
    
    def add_images(self, images: list[ChapterImage]) -> None:
        for image in images:
            self.add_image(image)

