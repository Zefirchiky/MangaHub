from pydantic import BaseModel
from .name_parsing import NameParsing
from .images_parsing import ImagesParsing


class MangaChapterParsing(BaseModel):
    images_parsing: ImagesParsing
    name_parsing: NameParsing | None = None