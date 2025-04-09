from ..tags.tag_model import TagModel
from pydantic import PrivateAttr


class ChapterImage(TagModel):
    number: int
    _image: bytes = PrivateAttr(b'')
    image_dir: str = ''