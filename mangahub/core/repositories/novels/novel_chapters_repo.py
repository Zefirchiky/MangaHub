from core.repositories.abstract.chapters_repository import ChaptersRepository
from core.models.novels import NovelChapter
from .paragraphs_repository import ParagraphsRepository


class ChapterNotFoundError(Exception): ...

class NovelChaptersRepository(ChaptersRepository[NovelChapter, ParagraphsRepository]):
    def __init__(self, file):
        super().__init__(file, NovelChapter, ParagraphsRepository)
