import os
from models import Manga, MangaChapter, ChapterImage, Site
from services.handlers import JsonHandler
from gui.gui_utils import MM


class ModelJsonParser:
    def __init__(self, file, model: Manga | MangaChapter | ChapterImage | Site):
        self.file = file
        self.model = model
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self.models_collection = {}
        
    def get_model(self, name) -> Manga | MangaChapter | ChapterImage | Site | None:
        if name in self.models_collection.keys():
            return self.models_collection[name]
        
        try:
            model = self.model.model_validate(self.data[name])
            self.models_collection[name] = model
            return model
        except KeyError:
            MM.show_message('error', f"{model.__name__} {name} not found")
            return None
        
    def get_all_models(self) -> dict[str | float, Manga | MangaChapter | ChapterImage | Site]:
        for name in self.data.keys():
            if name not in self.models_collection.keys():
                self.get_model(name)
                
        return self.models_collection
    
    def save(self, models_dict: dict[str, Manga | MangaChapter | ChapterImage | Site]):
        models_list = {name: model.model_dump(mode="json") for name, model in models_dict.items()}
        self.json_parser.save_data(models_list)