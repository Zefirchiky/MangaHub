from loguru import logger

from .models_json_parser import ModelsJsonParser
from .manga_chapters_parser import MangaChaptersParser
from models import Manga


class MangaParser(ModelsJsonParser):
    def __init__(self, file="data/manga.json"):
        super().__init__(file, Manga)
        self.manga_collection = self.models_collection

    def get_manga(self, name) -> Manga | None:
        return self.get_model(name)

    def get_all_manga(self) -> dict:
        return self.get_all_models()
    
    def save_manga(self, manga_dict: dict[str, Manga]):
        for manga in manga_dict.values():
            chapters_parser = MangaChaptersParser(manga)
            chapters_parser.save(manga._chapters_data)
        super().save(manga_dict)
        
        logger.success("All manga saved successfully")
