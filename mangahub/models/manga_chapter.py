from dataclasses import dataclass, field
from typing import Iterator, Dict


@dataclass
class MangaChapter:
    number: int
    name: str
    _id_dex: str = ''
    images: Dict[int, str] = field(default_factory=dict)

    def __iter__(self) -> Iterator[dict]:
        return iter(self.images.values())
    
    def set_id_dex(self, id_dex: str) -> None:
        self._id_dex = id_dex

    def add_image(self, num: int, image: str) -> None:
        self.images[num] = image

    def add_images(self, images: Dict[int, str]) -> None:
        for num, image in images.items():
            self.images[num] = image

    def set_all_images(self, images: Dict[int, str]) -> None:
        self.images = images