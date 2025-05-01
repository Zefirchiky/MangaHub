from models.manga import Manga
from services.parsers.models_json_parser import ModelsJsonParser
from .manga_chapters_repository import MangaChaptersRepository

from loguru import logger


class MangaRepository(ModelsJsonParser[str, Manga]):
    def __init__(self, file) -> None:
        super().__init__(file, Manga, str)

    def add(self, manga: Manga) -> dict[str, Manga]:
        self._models_collection[manga.name] = manga
        return self.models_collection

    def get(self, name) -> Manga | None:
        try:
            return super().get(name)

        except Exception as e:
            logger.warning(f"Manga {name} not found with error: {e}. Returning None")
            return None

    def load(self) -> dict[str, Manga]:  # TODO: Lazy chapters loading
        for manga in (mangas := super().get_all()).values():
            for chapter in MangaChaptersRepository(manga).get_all().values():
                manga.add_chapter(chapter)
        return mangas

    def save(self) -> None:
        for manga in self.models_collection.values():
            chapters_parser = MangaChaptersRepository(manga)
            chapters_parser.save(manga._chapters_data)
        super().save(self.models_collection)

        logger.success("All manga saved successfully")
