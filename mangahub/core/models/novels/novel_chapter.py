from core.interfaces import AbstractChapter
from .novel_paragraph import NovelParagraph


class NovelChapter(AbstractChapter[int, NovelParagraph]):
    @property
    def text(self) -> str:
        return '\n\n'.join([str(para) for para in self._repo.get_all().values()])