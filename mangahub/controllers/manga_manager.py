from directories import *
from gui.gui_utils import MM
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from services.scrapers import MangaSiteScraper
from services.scrapers import MangaDexScraper
from models import Manga, MangaChapter
from utils import BatchWorker, retry
import requests
import os

            
class MangaManager:
    def __init__(self, app):
        self.app = app
        self.manga_parser: MangaJsonParser = self.app.manga_json_parser
        self.sites_parser: SitesJsonParser = self.app.sites_json_parser
        self.dex_scraper = MangaDexScraper()
        self.sites_scraper = MangaSiteScraper(self.sites_parser)
        self.manga_collection = self.get_all_manga()
        
    @retry(max_retries=3, delay=1, exception_to_check=Exception)
    def get_manga(self, name):
        manga = self.manga_collection.get(name)
        if not manga:
            MM.show_message('error', f"Manga {name} not found")
            return None
        return manga
    
    def add_new_manga(self, manga: Manga):
        self.manga_collection[manga.name] = manga
        
    def create_manga(self, name, manga_dex=True):
        _id = name.lower().replace(' ', '-')
        cover = self.dex_scraper.get_manga_cover(_id_dex)
        _id_dex = self.get_manga_id_from_manga_dex(name) if manga_dex else None
        manga = Manga(name, _id, _id_dex=_id_dex)
        self.add_new_manga(manga)
        return manga
    
    @retry(max_retries=3, delay=1, exception_to_check=Exception)
    def get_chapter(self, manga, num):
        chapter = manga.chapters[num]
        if not chapter:
            MM.show_message('error', f"Chapter {manga.name} {num} not found")
            return None
        return chapter
        
    def get_manga_id_from_manga_dex(self, name):
        url = "https://api.mangadex.org/manga"
        params = {
            "title": name,
            "limit": 1
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data["data"]:
            manga = data["data"][0]
            return manga["id"]
        return None
    
    def get_chapter_id(self, num, manga_id, language="en"):
        url = f"https://api.mangadex.org/chapter"
        params = {
            "manga": manga_id,
            "translatedLanguage[]": language,
            "chapter": num,
            "limit": 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        chapter_id = data["data"][0]["id"]
        
        return chapter_id
    
    def get_chapter_images_url(self, chapter_id):
        url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        base_url = data["baseUrl"]
        image_files = data["chapter"]["dataSaver"]
        
        # Construct full image URLs
        image_urls = [f"{base_url}/data-saver/{data['chapter']['hash']}/{image_file}" for image_file in image_files]
        
        return image_urls
    
    def get_chapter_images(self, chapter: MangaChapter, manga_title, manga_dex=True):
        if manga_dex:
            self.scraper = MangaDexScraper()
            images = self.scraper.get_chapter_image_placeholders(chapter._id_dex), self.scraper.start_chapter_images_download(chapter._id_dex)
        else:
            self.scraper = MangaSiteScraper(self.sites_parser, self.manga_parser.get_manga(manga_title))
            images = self.scraper.get_chapter_images(chapter.number)
                            
        return images

    def get_manga_from_url(self, url):
        url_parser = UrlParser(url, self.sites_parser)
        site = url_parser.site
        _id = url_parser.get_manga_id()
        name = _id.title().replace('-', ' ')

        if not os.path.exists(f'{MANGA_DIR}/{_id}'):
            os.makedirs(f'{MANGA_DIR}/{_id}')
            
        cover = self.ensure_cover(_id, url_parser)

        return Manga(name, _id, cover, [site.name])
    
    def ensure_cover(self, _id, url_parser):
        dir = f'{MANGA_DIR}/{_id}'
        if os.path.exists(f'{dir}/cover.jpg'):
            cover = f'{dir}/cover.jpg'
        else:
            scraper = MangaSiteScraper(self.sites_parser, url_parser=url_parser)
            cover = scraper.save_manga_cover_path(dir)

        return cover
    
    def get_all_manga(self):
        return self.manga_parser.get_all_manga()
    
    def get_new_chapter(self, manga, num):
        _dir = f'data/manga/{manga._id}/chapter{num}'
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        scraper = MangaSiteScraper(self.sites_parser, manga=manga)
        chapter = MangaChapter(num, scraper.get_chapter_name(num))

        images = scraper.get_chapter_images(num)
        for i, image in enumerate(images):
            with open(f'{_dir}/{i + 1}.webp', 'wb') as f:
                f.write(image)
            chapter.add_image(i + 1, f'{_dir}/{i + 1}.webp')

        return chapter
    
    def add_chapter(self, manga: Manga, chapter: MangaChapter):
        manga.add_chapter(chapter)
    
    def get_chapter_images_iter(self, manga, num):
        scraper = MangaSiteScraper(self.sites_parser, manga=manga)