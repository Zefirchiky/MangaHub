from typing import ClassVar
from ..tags.tag_model import TagModel
from ..images import ImageMetadata, ImageCache


class ChapterImage(TagModel):
    _cache: ClassVar[ImageCache] = None
    number: int
    metadata: ImageMetadata = None
    image_dir: str = ""

    # def get_image(self) -> bytes:
    #     return self._cache.get_image
