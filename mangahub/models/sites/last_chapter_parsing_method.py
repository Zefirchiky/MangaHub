from pydantic import BaseModel


class LastChapterParsingMethod(BaseModel):
    string_format: str
    on_title_page: bool = False
    on_chapter_page: int = 0
