from typing import ClassVar
from pathlib import Path
from ..tags.tag_model import TagModel
from ..images import ImageMetadata, ImageCache


class ChapterImage(TagModel):
    _cache: ClassVar[ImageCache] = None
    number: int
    name: str = ''
    metadata: ImageMetadata = None
    image_dir: Path = ''

    # def get_image(self) -> bytes:
    #     return self._cache.get_image
