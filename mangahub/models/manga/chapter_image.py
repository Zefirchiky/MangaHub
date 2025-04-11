from ..tags.tag_model import TagModel
from ..images import ImageMetadata
from pydantic import PrivateAttr


class ChapterImage(TagModel):
    number: int
    _image: bytes = PrivateAttr(b'')
    metadata: ImageMetadata = None
    image_dir: str = ''