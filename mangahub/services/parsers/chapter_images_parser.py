from models.manga import ChapterImage

from .models_json_parser import ModelsJsonParser


class ChapterImagesParser(ModelsJsonParser[int, ChapterImage]):
    def __init__(self, file):
        super().__init__(file, ChapterImage, int)
