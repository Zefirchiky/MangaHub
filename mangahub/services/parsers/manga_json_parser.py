from typing import Dict
from services.handlers import JsonHandler
from models import Manga, MangaChapter
from gui.gui_utils import MM


class MangaJsonParser:
    def __init__(self, file="data/manga.json"):
        self.file = file
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self.manga_collection = {}

    def get_manga(self, name) -> Manga | None:
        if name in self.manga_collection.keys():
            return self.manga_collection[name]
        else:
            try:
                manga = Manga.model_validate(self.data[name])
                self.manga_collection[name] = manga
                return manga
            except KeyError:
                MM.show_message('error', f"Manga {name} not found")
                return None

    def get_all_manga(self) -> dict:
        for manga_name in self.data.keys():
            if manga_name not in self.manga_collection.keys():
                self.manga_collection[manga_name] = self.get_manga(manga_name)
        
        return self.manga_collection
    
    def save_manga(self, manga_dict: Dict[str, Manga]):
        manga_list = {name: manga.model_dump(mode="json") for name, manga in manga_dict.items()}
        self.json_parser.save_data(manga_list)
