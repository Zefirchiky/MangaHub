from directories import *
from gui.gui_utils import MM
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from services.scrapers import MangaSiteScraper, MangaDexScraper
from services.handlers import JsonHandler
from models import Manga, MangaChapter, ChapterImage
from utils import retry
import os

            
class MangaManager:
    def __init__(self, app):
        self.app = app
        self.manga_parser: MangaJsonParser = self.app.manga_json_parser
        self.sites_parser: SitesJsonParser = self.app.sites_json_parser
        self.dex_scraper = MangaDexScraper()
        self.sites_scraper = MangaSiteScraper(self.sites_parser)
        self.manga_collection = self.get_all_manga()
        
    def get_manga(self, name) -> Manga | None:
        manga = self.manga_collection.get(name)
        if not manga:
            MM.show_message('error', f"Manga {name} not found")
            raise Exception(f"Manga {name} not found")
        return manga
    
    def add_new_manga(self, manga: Manga):
        self.manga_collection[manga.name] = manga
        
    def create_manga(self, name, site='MangaDex', backup_sites=[], **kwargs):
        id_ = name.lower().replace(' ', '-').replace(',', '').replace('.', '')
        id_dex = self.dex_scraper.get_manga_id(name)
        folder = f'{MANGA_DIR}/{id_}'
        os.makedirs(folder, exist_ok=True)
        last = self.dex_scraper.get_last_chapter_num(id_dex)
        
        manga = Manga(name=name, id_=id_, id_dex=id_dex, folder=folder, last_chapter=last, site=site, backup_sites=backup_sites, **kwargs)
        # manga.add_chapter(self.get_chapter(manga, 1))
        # manga.add_chapter(self.get_chapter(manga, last))
        
        cover = self.ensure_cover(manga)
        manga.cover = cover
        
        self.add_new_manga(manga)
        return manga
    
    def get_chapter(self, manga: Manga, num):
        json = JsonHandler(f"{manga.folder}/chapters.json").get_data()
        if json.get(num):
            return json[num]
        
        chapter = manga._chapters_data.get(num)
        if chapter:
            return chapter
        
        _id_dex = self.dex_scraper.get_chapter_id(manga.id_dex, num)
        name = self.dex_scraper.get_chapter_name(manga.id_dex, num)
        # if not name:
        #     self.sites_scraper.get_chapter_name(manga, num)
        
        upload_date = self.dex_scraper.get_chapter_upload_date(manga.id_dex, num)
        chapter = MangaChapter(number=num, name=name, id_dex=_id_dex, upload_date=upload_date)
        return chapter
    
    def get_image(self, chapter: MangaChapter, num):
        image = chapter.images.get(num)
        if image:
            return image
        
        width, height = self.dex_scraper.get_image_size(chapter.id_dex, num)
        image = ChapterImage(num, width, height)
        return image
    
    def get_chapter_images(self, manga: Manga, chapter: MangaChapter, manga_dex=True):
        if manga_dex and chapter.id_dex:
            placeholders, images = self.dex_scraper.get_chapter_placeholders(chapter.id_dex), self.dex_scraper.start_chapter_images_download(chapter.id_dex)
            if not placeholders:
                placeholders = self.sites_scraper.get_chapter_placeholders(manga, chapter.number)
            if not images:
                images = self.sites_scraper.start_chapter_images_download(manga, chapter.number)
        else:
            placeholders, images = self.sites_scraper.get_chapter_placeholders(manga, chapter.number), self.sites_scraper.start_chapter_images_download(manga, chapter.number)

        if not placeholders:
            MM.show_message('warning', f"Placeholders wasn't parsed successfully for {manga.name}")
            return None

        if not images:
            MM.show_message('warning', f"Images wasn't parsed successfully for {manga.name}")
            return []

        return placeholders, images

    def get_manga_from_url(self, url):
        url_parser = UrlParser(url, self.sites_parser)
        site = url_parser.site
        _id = url_parser.get_manga_id()
        name = _id.title().replace('-', ' ')

        if not os.path.exists(f'{MANGA_DIR}/{_id}'):
            os.makedirs(f'{MANGA_DIR}/{_id}')
            
        cover = self.ensure_cover(_id, url_parser)

        return Manga(name, _id, cover, [site.name])
    
    def ensure_cover(self, manga: Manga):
        if os.path.exists(f'{manga.folder}/cover.jpg'):
            return f'cover.jpg'
        
        if manga.id_dex:
            cover = self.dex_scraper.get_manga_cover(manga.id_dex)
        elif manga.backup_sites:
            scraper = MangaSiteScraper(self.sites_parser, sites=manga.backup_sites)
            cover = scraper.get_manga_cover(manga)  # TODO
        else:
            MM.show_message('error', f"No available site for {manga.id_} was found")
            return None
        
        if cover:    
            with open(f'{manga.folder}/cover.jpg', 'wb') as f:
                f.write(cover)

            return f'cover.jpg'
        return None
    
    def get_all_manga(self) -> dict[str, Manga]:
        return self.manga_parser.get_all_manga()
    
    def add_chapter(self, manga: Manga, chapter: MangaChapter):
        manga.add_chapter(chapter)
        
    def save(self):
        self.manga_parser.save_manga(self.manga_collection)