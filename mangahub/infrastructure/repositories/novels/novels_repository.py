from domain.models.novels import Novel
from services.parsers import TagModelsJsonParser


class NovelsRepository(TagModelsJsonParser[str, Novel]):
    def __init__(self, file) -> None:
        super().__init__(file, Novel, str)