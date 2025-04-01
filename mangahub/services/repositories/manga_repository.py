from models.manga import Manga
from services.parsers.models_json_parser import ModelsJsonParser
from services.parsers.manga_chapters_parser import MangaChaptersParser

from loguru import logger


class MangaRepository(ModelsJsonParser):
    def __init__(self, file) -> None:
        super().__init__(file, Manga)

    def add(self, manga: Manga) -> dict[str, Manga]:
        self._models_collection[manga.name] = manga
        return self.models_collection

    def get(self, name) -> Manga | None:
        try:
            return super().get_model(name)
        except Exception as e:
            logger.warning(f"Manga {name} not found with error: {e}. Returning None")
            return None

    def get_all(self) -> dict[str, Manga]:
        return self.models_collection
    
    def load(self) -> dict[str, Manga]:
        return super().get_all_models()
    
    def save(self) -> None:
        for manga in self.models_collection.values():
            chapters_parser = MangaChaptersParser(manga)
            chapters_parser.save(manga._chapters_data)
        super().save(self.models_collection)
        
        logger.success("All manga saved successfully")