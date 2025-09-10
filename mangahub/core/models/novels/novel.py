from enchant import Dict
from core.interfaces import AbstractMedia
# from core.repositories.novels import NovelChaptersRepository
from .novel_chapter import NovelChapter


class Novel(AbstractMedia[NovelChapter]):
    dictionary: object = Dict('en_us')
    
    @property
    def text(self) -> str:
        text = ""
        for i, chapter in enumerate(self._chapters_repo.get_all().values()):
            if i != 0:
                text += "\n\n\t"
            text += chapter.text
        return text
