from .manga_chapter_image import MangaChapterImage
from dataclasses import dataclass, field
from typing import Iterator, List


@dataclass
class MangaChapter:
    number: int
    name: str
    images: List[MangaChapterImage] = field(default_factory=list)

    def __iter__(self) -> Iterator[MangaChapterImage]:
        return iter(self.images)

    def add_image(self, image: MangaChapterImage) -> None:
        self.images.append(image)

    def add_images(self, images: List[MangaChapterImage]) -> None:
        for image in images:
            self.images.append(image)

    def add_all_images(self, images: List[MangaChapterImage]) -> None:
        self.images = images