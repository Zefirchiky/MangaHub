from models import ChapterImage
from .model_json_parser import ModelJsonParser


class ChapterImagesJsonParser(ModelJsonParser):
    def __init__(self, file):
        super().__init__(file, ChapterImage)
        
    def get_all_images(self) -> dict[float, ChapterImage]:
        return self.get_all_models()