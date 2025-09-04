from ..abstract.chapters_repository import ChaptersRepository
from .images_data_repository import ImagesDataRepository
from core.models.manga import MangaChapter


class MangaChaptersRepository(ChaptersRepository[MangaChapter]):
    def __init__(self, file):
        super().__init__(file, MangaChapter)

    def get(self, name) -> MangaChapter | None:
        chapter = super().get(name)
        if chapter and chapter.get_data_repo() is None:
            chapter.set_data_repo(ImagesDataRepository(
                chapter.folder / 'images.json'
            ))
            
        return chapter
