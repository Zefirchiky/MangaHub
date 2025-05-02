from pydantic import PrivateAttr

from ..abstract.abstract_media import AbstractMedia
from .novel_chapter import NovelChapter


class Novel(AbstractMedia[NovelChapter]):
    _chapters_data: dict[int | float, NovelChapter] = PrivateAttr(default_factory=dict)

    @property
    def text(self) -> str:
        text = ""
        for i, chapter in enumerate(self._chapters_data.values()):
            if i != 0:
                text += "\n\n\t"
            text += chapter.text
        return text
