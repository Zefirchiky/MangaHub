from services.scrapers import MangaSiteScraper, get_name_identifier_from_url
from models import Manga
import os


class MangaManager:
    def __init__(self):
        pass

    def get_manga_from_url(self, url):
        self.scraper = MangaSiteScraper(url=url)
        site = self.scraper.site
        _id = get_name_identifier_from_url(site, url)[0]
        name = _id.title().replace('-', ' ')

        if not os.path.exists(f'mangamanager/data/manga/{_id}'):
            os.makedirs(f'mangamanager/data/manga/{_id}')
            
        cover = self.ensure_cover(_id)

        return Manga(name, _id, cover, [site.name])
    
    def ensure_cover(self, _id):            
        if os.path.exists(f'mangamanager/data/manga/{_id}/cover.jpg'):
            cover = f'mangamanager/data/manga/{_id}/cover.jpg'
        else:
            cover = self.scraper.save_manga_cover_path(f'mangamanager/data/manga/{_id}')

        return cover
