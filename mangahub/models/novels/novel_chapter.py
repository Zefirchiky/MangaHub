from __future__ import annotations
from pydantic import PrivateAttr
from ..abstract.abstract_chapter import AbstractChapter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.repositories.novels import ParagraphsRepository 


class NovelChapter(AbstractChapter):
    _paragraphs_data = PrivateAttr(default=None)

    @property
    def text(self) -> str:
        text = ""
        for i, chapter in self._paragraphs_data.get_all().items():
            if i != 0:
                text += "\n\n"
            text += str(chapter.sentences)
        return text
    
    def set_data_repo(self, repo: ParagraphsRepository):
        self._paragraphs_data = repo
        return self
        
    def get_data_repo(self) -> ParagraphsRepository:
        return self._paragraphs_data