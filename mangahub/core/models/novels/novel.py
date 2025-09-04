from ..abstract.abstract_media import AbstractMedia
from .novel_chapter import NovelChapter


class Novel(AbstractMedia[NovelChapter]):
    @property
    def text(self) -> str:
        text = ""
        for i, chapter in enumerate(self._chapters_repo.get_all().values()):
            if i != 0:
                text += "\n\n\t"
            text += chapter.text
        return text
