from services.handlers import JsonHandler
from models import Manga


class MangaJsonParser:
    def __init__(self, file="mangamanager/data/manga.json"):
        self.file = file
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
    
    def get_all_manga(self):
        _manga = []
        
        for manga in self.data:
            _manga.append(Manga(self.data[manga]['name'], self.data[manga]['id'], self.data[manga]['cover'], self.data[manga]['sites'], self.data[manga]['chapters']))

        return _manga