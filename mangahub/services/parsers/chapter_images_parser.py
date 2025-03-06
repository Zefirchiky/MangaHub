from models.manga import ChapterImage
from .models_json_parser import ModelsJsonParser


class ChapterImagesParser(ModelsJsonParser):
    def __init__(self, file):
        super().__init__(file, ChapterImage)
        
    def get_all_images(self) -> dict[float, ChapterImage]:
        return self.get_all_models()    # type: ignore