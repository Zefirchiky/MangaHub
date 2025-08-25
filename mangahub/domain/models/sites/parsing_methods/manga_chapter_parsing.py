from pydantic import BaseModel
from .parsing_method import ParsingMethod
from .name_parsing import NameParsing
from .images_parsing import ImagesParsing


class MangaChapterParsing(BaseModel):
    images_parsing: ImagesParsing
    name_parsing: NameParsing | None = None
    
    def get_parsing_methods(self) -> list[ParsingMethod]:
        result = [
            self.images_parsing
        ]
        if self.name_parsing:
            result.append(self.name_parsing)
        return result