from ..handlers import MangaJsonParser
import requests # type: ignore


class MangaScraper:
    def __init__(self, url: str):
        self.url = url

    def get_title_page(self):
        return requests.get(self.url)
    
    def get_chapter_page(self):
        pass