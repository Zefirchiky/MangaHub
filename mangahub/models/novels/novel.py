from pydantic import PrivateAttr
from .novel_chapter import NovelChapter
from ..abstract.abstract_media import AbstractMedia


class Novel(AbstractMedia):
    _chapters_data: dict[int | float, NovelChapter] = PrivateAttr(default_factory=dict)
    
    def add_chapter(self, chapter: NovelChapter) -> None:
        super().add_chapter(chapter)