from services.handlers import JsonHandler
from models import Manga


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
                manga = Manga(**self.data[name])
                self.manga[name] = manga
                return manga
            except KeyError:
                raise Exception(f"Manga {name} not found")

    def get_all_manga(self) -> dict:
        for manga_name, manga in self.data.items():
            if manga_name not in self.manga.keys():
                self.manga[manga_name] = self.get_manga(manga_name)
        
        return self.manga
