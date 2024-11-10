from pydantic import BaseModel
from .tags.tag_model import TagModel


class ChapterImage(TagModel, BaseModel):
    number: int
    width: int
    height: int
    image: str = ''