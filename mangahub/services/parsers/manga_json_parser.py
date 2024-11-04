from dataclasses import asdict
from services.handlers import JsonHandler
from models import Manga, MangaChapter, ChapterImage


class MangaJsonParser:
    def __init__(self, file="data/manga.json"):
        self.file = file
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self.manga = {}

    def get_manga(self, name) -> Manga | None:
        if name in self.manga.keys():
            return self.manga[name]
        else:
            try:
                for num, chapter in self.data[name]["chapters"].copy().items():
                    if isinstance(num, str):
                        del self.data[name]["chapters"][num]
                    self.data[name]["chapters"][int(num)] = MangaChapter(**chapter)
                manga = Manga(**self.data[name])
                self.manga[name] = manga
                return manga
            except KeyError:
                raise Exception(f"Manga {name} not found")

    def get_all_manga(self) -> dict:
        for manga_name in self.data.keys():
            if manga_name not in self.manga.keys():
                self.manga[manga_name] = self.get_manga(manga_name)
        
        return self.manga
    
    def save_data(self, data):
        manga_list = {manga.name: asdict(manga) for manga in data.values()}
        self.json_parser.save_data(manga_list)
