from models import Manga
from services.parsers.models_json_parser import ModelsJsonParser
from directories import MANGA_JSON


class MangaRepository(ModelsJsonParser):
    def __init__(self, file=MANGA_JSON) -> None:
        super().__init__(file, Manga)

    def add_manga(self, manga: Manga) -> None:
        self._models_collection[manga.name] = manga

    def get_manga(self, name) -> Manga:
        return super().get_model(name)

    def get_all(self) -> dict[str, Manga]:
        return self._models_collection
    
    def load(self) -> dict[str, Manga]:
        return super().get_all_models()