from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from services.scrapers import MangaSiteScraper
from models import Manga, MangaChapter
from directories import *
import os


class MangaManager:
    def __init__(self, manga_parser: MangaJsonParser, sites_parser: SitesJsonParser):
        self.manga_parser = manga_parser
        self.sites_parser = sites_parser

        self.manga = self.get_all_manga()

    def get_manga_from_url(self, url):
        url_parser = UrlParser(url, self.sites_parser)
        site = url_parser.site
        _id = url_parser.get_manga_id()
        name = _id.title().replace('-', ' ')

        if not os.path.exists(f'data/manga/{_id}'):
            os.makedirs(f'data/manga/{_id}')
            
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

    def get_manga(self, name):
        print(self.manga)
        return self.manga[name]
    
    def get_chapter(self, manga, num):
        return manga.chapters[num]
    
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
        print(chapter)

        return chapter
    
    def add_chapter(self, manga: Manga, chapter: MangaChapter):
        manga.add_chapter(chapter)
    
    def get_chapter_images_iter(self, manga, num):
        scraper = MangaSiteScraper(self.sites_parser, manga=manga)