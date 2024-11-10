from .model_json_parser import ModelJsonParser
from .manga_chapters_json_parser import MangaChaptersJsonParser
from models import Manga


class MangaJsonParser(ModelJsonParser):
    def __init__(self, file="data/manga.json"):
        super().__init__(file, Manga)
        self.manga_collection = self.models_collection

    def get_manga(self, name) -> Manga | None:
        return self.get_model(name)

    def get_all_manga(self) -> dict:
        return self.get_all_models()
    
    def save_manga(self, manga_dict: dict[str, Manga]):
        for manga in manga_dict.values():
            chapters_parser = MangaChaptersJsonParser(manga)
            chapters_parser.save(manga._chapters_data)
        super().save(manga_dict)
