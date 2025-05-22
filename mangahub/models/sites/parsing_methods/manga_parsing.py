from pydantic import BaseModel
from .parsing_method import ParsingMethod
from .name_parsing import NameParsing
from .cover_parsing import CoverParsing
from .last_chapter_parsing import ChaptersListParsing
from .images_parsing import ImagesParsing


class MangaParsing(BaseModel):
    name_parsing: NameParsing
    cover_parsing: CoverParsing
    last_chapter_parsing: ChaptersListParsing
    
    def get_parsing_methods(self) -> list[ParsingMethod]:
        return [
            self.name_parsing,
            self.cover_parsing,
            self.last_chapter_parsing,
        ]