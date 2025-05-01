from models.novels import Novel
from services.parsers.models_json_parser import ModelsJsonParser


class NovelsRepository(ModelsJsonParser[str, Novel]):
    def __init__(self, file) -> None:
        super().__init__(file, Novel, str)

    def add(self, novel: Novel) -> dict[str, Novel]:
        self._models_collection[novel.name] = novel
        return self._models_collection

    def get_all(self) -> dict[str, Novel]:
        return self._models_collection

    def load(self) -> dict[str, Novel]:
        return super().get_all()
