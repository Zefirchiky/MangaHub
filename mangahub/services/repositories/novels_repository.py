from models import Novel
from services.parsers.models_json_parser import ModelsJsonParser
from directories import NOVELS_JSON


class NovelsRepository(ModelsJsonParser):
    def __init__(self, file=NOVELS_JSON) -> None:
        super().__init__(file, Novel)

    def add_novel(self, Novel: Novel) -> None:
        self._models_collection[Novel.name] = Novel

    def get_novel(self, name) -> Novel:
        return super().get_model(name)

    def get_all(self) -> dict[str, Novel]:
        return self._models_collection
    
    def load(self) -> dict[str, Novel]:
        return super().get_all_models()