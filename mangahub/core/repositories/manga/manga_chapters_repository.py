from core.repositories.abstract import ChaptersRepository
from .images_data_repository import ImagesDataRepository
from core.models.manga.manga_chapter import MangaChapter


class ChapterNotFoundError(Exception): ...

class MangaChaptersRepository(ChaptersRepository[MangaChapter, ImagesDataRepository]):
    def __init__(self, file):
        super().__init__(file, MangaChapter, ImagesDataRepository)
