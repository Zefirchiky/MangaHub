from PySide6.QtCore import QObject
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from services.scrapers import MangaSiteScraper
from models import Manga, MangaChapter
from utils import BatchWorker
from directories import *
from gui.gui_utils import MessageManager
import requests
import os

            
class MangaManager:
    def __init__(self, app):
        self.app = app
        self.manga_parser = self.app.manga_json_parser
        self.sites_parser = self.app.sites_json_parser

        self.manga = self.get_all_manga()
        
    def get_manga(self, name, manga_dex=True):
        if name in self.manga.keys():
            return self.manga[name]
        else:
            raise Exception(f"Manga {name} not found")
        
    def get_chapter(self, manga, num):
        if num in manga.chapters.keys():
            return manga.chapters[num]
        else:
            self.app.mm.show_message('error', f"Chapter {num} not found")
        
    def get_manga_id_from_manga_dex(self, name):
        url = "https://api.mangadex.org/manga"
        params = {
            "title": name,
            "limit": 1
        }
        response = requests.get(url, params=params)
        MessageManager.get_instance().show_message('error', f"Manga {name} not found")
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
    
    def get_manga_chapter_images(self, manga_title, num):
        manga_id = self.get_manga_id_from_manga_dex(manga_title)
        if not manga_id:
            return None
        
        chapter_id = self.get_chapter_id(num, manga_id)
        image_urls = self.get_chapter_images_url(chapter_id)
        images = []
        
        worker = BatchWorker()
        worker.signals.all_completed.connect(lambda _: MessageManager.get_instance().show_message('info', 'Images downloaded'))
        
        for image in worker.process_batch(requests.get, image_urls):
            images.append(image.content)
                
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