from directories import *
from gui.gui_utils import MM
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from services.scrapers import MangaSiteScraper
from services.scrapers import MangaDexScraper
from models import Manga, MangaChapter, ChapterImage
from utils import BatchWorker, retry
import datetime
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
    def get_manga(self, name) -> Manga | None:
        manga = self.manga_collection.get(name)
        if not manga:
            MM.show_message('error', f"Manga {name} not found")
            return None
        return manga
    
    def add_new_manga(self, manga: Manga):
        self.manga_collection[manga.name] = manga
        self.manga_parser.save_data(self.manga_collection)
        
    def create_manga(self, name, sites=[]):
        _id = name.lower().replace(' ', '-')
        _id_dex = self.dex_scraper.get_manga_id(name)
        last = self.dex_scraper.get_last_chapter_num(_id_dex)
        
        cover = f'{MANGA_DIR}/{_id}/cover.jpg'
        os.makedirs(f'{MANGA_DIR}/{_id}', exist_ok=True)
        with open(cover, 'wb') as f:
            f.write(self.dex_scraper.get_manga_cover(_id))
        
        manga = Manga(name, _id, _id_dex, cover, last_chapter=last, sites=sites)
        manga.add_chapter(self.get_chapter(manga, 1))
        manga.add_chapter(self.get_chapter(manga, last))
        return manga
    
    def get_chapter(self, manga: Manga, num):
        chapter = manga.chapters.get(num)
        if chapter:
            return chapter
        
        _id_dex = self.dex_scraper.get_chapter_id(manga._id_dex, num)
        name = self.dex_scraper.get_chapter_name(manga._id_dex, num)
        if not name:
            self.sites_scraper.get_chapter_name(manga, num)
        
        upload_date = self.dex_scraper.get_chapter_upload_date(manga._id_dex, num)
        chapter = MangaChapter(num, name, _id_dex, upload_date=upload_date)
        return chapter
    
    def get_image(self, chapter: MangaChapter, num):
        image = chapter.images.get(num)
        if image:
            return image
        
        width, height = self.dex_scraper.get_image_size(chapter._id_dex, num)
        image = ChapterImage(num, width, height)
        return image
    
    def get_chapter_images(self, manga: Manga, chapter: MangaChapter, manga_dex=True):
        if manga_dex and chapter._id_dex:
            images = self.dex_scraper.get_chapter_placeholders(chapter._id_dex), self.dex_scraper.start_chapter_images_download(chapter._id_dex)
        else:
            images = self.sites_scraper.get_chapter_placeholders(manga, chapter.number), self.sites_scraper.start_chapter_images_download(manga, chapter.number)

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