from ..abstract.chapter_data_repository import ChapterDataRepository
from core.models.novels import NovelParagraph


class ParagraphsRepository(ChapterDataRepository[int, NovelParagraph]):
    def __init__(self, file):
        super().__init__(file, NovelParagraph, int)