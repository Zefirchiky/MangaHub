from core.repositories.abstract.media_repository import MediaRepository
from .manga_chapters_repository import MangaChaptersRepository
from core.models.manga.manga import Manga, MangaChapter


class MangaRepository(MediaRepository[Manga, MangaChapter, MangaChaptersRepository]):
    def __init__(self, file) -> None:
        super().__init__(file, Manga, MangaChapter, MangaChaptersRepository)
