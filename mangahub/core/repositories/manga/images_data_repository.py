from ..abstract.chapter_data_repository import ChapterDataRepository
from core.models.manga import ChapterImage


class ImagesDataRepository(ChapterDataRepository[int, ChapterImage]):
    def __init__(self, file):
        super().__init__(file, ChapterImage, int)