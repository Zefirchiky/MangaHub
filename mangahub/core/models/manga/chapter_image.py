from pathlib import Path
from ..tags.tag_model import TagModel
from ..images import ImageMetadata


class ChapterImage(TagModel):
    number: int
    name: str = ''
    metadata: ImageMetadata = None
    image_dir: Path = ''
