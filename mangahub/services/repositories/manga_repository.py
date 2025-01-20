from models.manga import Manga
from services.parsers.models_json_parser import ModelsJsonParser


class MangaRepository(ModelsJsonParser):
    def __init__(self, file) -> None:
        super().__init__(file, Manga)

    def add(self, manga: Manga) -> dict[str, Manga]:
        self._models_collection[manga.name] = manga
        return self._models_collection

    def get(self, name) -> Manga:
        return super().get_model(name)

    def get_all(self) -> dict[str, Manga]:
        return self._models_collection
    
    def load(self) -> dict[str, Manga]:
        return super().get_all_models()