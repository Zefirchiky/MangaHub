from ..abstract.abstract_chapter import AbstractChapter
from .novel_paragraph import NovelParagraph


class NovelChapter(AbstractChapter):
    _paragraphs_data: list[NovelParagraph] = []

    @property
    def text(self) -> str:
        text = ""
        for i, chapter in enumerate(self._paragraphs_data):
            if i != 0:
                text += "\n\n\t"
            text += chapter.elements
        return text
