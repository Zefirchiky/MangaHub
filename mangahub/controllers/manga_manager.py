import os
import shutil
from typing import TYPE_CHECKING

from directories import MANGA_DIR
from loguru import logger
from models import URL
from models.manga import ChapterImage, Manga, MangaChapter
from services.parsers import MangaChaptersParser, UrlParser
from services.repositories import MangaRepository
from services.scrapers import MangaDexScraper, MangaSiteScraper
from utils import MM

from .sites_manager import SitesManager

if TYPE_CHECKING:
    from mangahub.main import App
    
    
# TODO: reimplement

            
class MangaManager:
    def __init__(self, app: 'App'):
        self.app = app
        self.repository: MangaRepository = self.app.manga_repository
        self.repository.load()
        self.sites_manager: SitesManager = self.app.sites_manager
        self.dex_scraper = MangaDexScraper()
        self.sites_scraper = MangaSiteScraper(self.sites_manager)
        self.manga_collection: dict[str, Manga] = {}
        self.manga_collection = self.get_all_manga()
        
        logger.success('MangaManager initialized')
        
    def get_manga(self, name) -> Manga | None:
        manga = self.repository.get(name)
        if not manga:
            MM.show_message('warning', f"Manga {name} not found")
            logger.warning(f"Manga {name} not found")
        return manga
    
    def get_all_manga(self) -> dict[str, Manga]:
        if self.manga_collection:
            return self.manga_collection
        
        self.manga_collection = self.repository.get_all()
        for manga in self.manga_collection.values():
            if not manga._chapters_data.get(1):
                manga.add_chapter(self.get_chapter(manga, 1))
            if not manga._chapters_data.get(manga.last_chapter):
                manga.add_chapter(self.get_chapter(manga, manga.last_chapter))
            if manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter and \
                manga.current_chapter and not manga._chapters_data.get(manga.current_chapter):
                manga.add_chapter(self.get_chapter(manga, manga.current_chapter))
                
        return self.manga_collection
    
    def add_new_manga(self, manga: Manga):
        self.manga_collection[manga.name] = manga
        
    def create_manga(self, name: str, url: str | URL='', site='MangaDex', backup_sites=[], **kwargs):
        if self.get_manga(name):
            MM.show_message('warning', f"Manga {name} already exists")
            logger.warning(f"Manga {name} already exists")
            return
        
        if url:
            url = URL(url)
            site = self.sites_manager.get_site(url=url)
            if site:
                site = site.name
            else:
                raise Exception('Site not found')
            
        id_ = name.lower().replace(' ', '-').replace(',', '').replace('.', '').replace('?', '').replace('!', '')
        id_dex = self.dex_scraper.get_manga_id(name)
        folder = f'{MANGA_DIR}/{id_}'
        os.makedirs(folder, exist_ok=True)
        if id_dex:
            last = self.dex_scraper.get_last_chapter_num(id_dex)
        
        if site != 'MangaDex':
            backup_sites = list(backup_sites)
            backup_sites.insert(0, 'MangaDex')
            
        if site in backup_sites:
            backup_sites.remove(site)
        
        manga = Manga(name=name, id_=id_, id_dex=id_dex, folder=folder, last_chapter=last, site=site, backup_sites=backup_sites, **kwargs)
        
        if not id_dex or not last:
            last = self.sites_scraper.get_last_chapter_num(self.sites_manager.get_site(site), manga)
            if last:
                manga.last_chapter = last
                
        cover = self.ensure_cover(manga)
        manga.cover = cover
        
        self.add_new_manga(manga)
        if site != 'MangaDex':
            self.sites_manager.get_site(manga.site).add_manga(manga)    # type: ignore
        for site in manga.backup_sites:
            if site != 'MangaDex':
                site_ = self.sites_manager.get_site(manga.site)
                if site_:
                    site_.add_manga(manga)
                
        logger.success(f"Manga '{manga.name}' created")
        return manga
    
    def remove_manga(self, manga: Manga | str) -> Manga:
        if isinstance(manga, str):
            manga_name = manga
            manga = self.manga_collection.get(manga)
        if manga:
            shutil.rmtree(manga.folder)
            mg = self.manga_collection.pop(manga.name)
            site = self.sites_manager.get_site(manga.site)
            if site: 
                site.remove_manga(manga)
            else: 
                logger.warning(f"Site {manga.site} of manga '{manga.name}' not found while removing")
                raise Exception(f"Site {manga.site} of manga '{manga.name}' not found while removing")
            logger.success(f"Manga '{manga.name}' successfully removed")
            MM.show_message('success', f"Manga '{manga.name}' successfully removed")
            return mg
        
        logger.warning(f"Manga '{manga_name}' was not found for deletion")
        return
        
    def get_chapter(self, manga: Manga, num: float):
        chapter = manga._chapters_data.get(num)
        if chapter:
            return chapter
        
        chapter = MangaChaptersParser(manga).get_chapter(num)
        if chapter:
            return chapter
        
        id_dex = self.dex_scraper.get_chapter_id(manga.id_dex, num)
        name = ''
        if manga.site == 'MangaDex':
            if id_dex:
                name = self.dex_scraper.get_chapter_name(manga.id_dex, num)
            else:
                logger.warning(f"No id_dex for chapter {num} of '{manga.name}'")
        else:
            name = self.sites_scraper.get_chapter_name(self.sites_manager.get_site(manga.site), manga, num)
        
        upload_date = self.dex_scraper.get_chapter_upload_date(manga.id_dex, num)
        chapter = MangaChapter(number=num, name=name, id_dex=id_dex, upload_date=upload_date)
        return chapter
    
    def get_image(self, chapter: MangaChapter, num):
        image = chapter.images.get(num)
        if image:
            return image
        
        width, height = self.dex_scraper.get_image_size(chapter.id_dex, num)
        image = ChapterImage(num, width, height)
        return image
    
    def get_chapter_images(self, manga: Manga, chapter: MangaChapter):
        logger.info(f"Getting images for '{manga.name}' chapter {chapter.number}")
        
        sites = list(manga.backup_sites)
        sites.insert(0, manga.site)
        images = []
        for site in sites:
            if site == 'MangaDex':
                if not chapter.id_dex:
                    chapter.id_dex = self.dex_scraper.get_chapter_id(manga.id_dex, chapter.number)
                    if not chapter.id_dex:
                        logger.warning(f"No id_dex for chapter {chapter.number} of '{manga.name}'")
                        continue
                    logger.success(f"Got id_dex for '{manga.name}' chapter {chapter.number}")
                    
                images = self.dex_scraper.get_chapter_images(chapter.id_dex)
            else:
                images = self.sites_scraper.get_chapter_images(self.sites_manager.get_site(site), manga, chapter.number)
                
            if images:
                break
            if site == manga.site:
                logger.warning(f"Images wasn't parsed successfully for main site {site} of manga '{manga.name}'")
                MM.show_message('warning', f"Images wasn't parsed successfully for main site {site} of manga '{manga.name}'")
                
        if not images:
            logger.warning(f"Images wasn't parsed successfully for manga '{manga.name}'")
            MM.show_message('warning', f"Images wasn't parsed successfully for manga '{manga.name}'")
            return

        logger.success(f"Got images for '{manga.name}' chapter {chapter.number}")
        return images
    
    def get_chapter_placeholders(self, manga: Manga, chapter: MangaChapter):
        placeholders = []
        if chapter._images:
            for image in chapter._images.values():
                placeholders.append((image.width, image.height))
            logger.success(f"Got placeholders for '{manga.name}' chapter {chapter.number} from cache")
            return placeholders
        
        logger.info(f"Downloading placeholders for '{manga.name}' chapter {chapter.number}")
        sites = list(manga.backup_sites)
        sites.insert(0, manga.site)
        for site in sites:
            if site == 'MangaDex':
                if not chapter.id_dex:
                    logger.warning(f"No id_dex for chapter {chapter.number} of '{manga.name}'")
                    continue
                placeholders = self.dex_scraper.get_chapter_placeholders(chapter.id_dex)
            else:
                placeholders = self.sites_scraper.get_chapter_placeholders(self.sites_manager.get_site(site), manga, chapter.number)
                
            if placeholders:
                break
            if site == manga.site:
                logger.warning(f"Placeholders wasn't parsed successfully for main site {site} of manga '{manga.name}'")
                MM.show_message('warning', f"Placeholders wasn't parsed successfully for main site {site} of manga '{manga.name}'")
                
        if not placeholders:
            logger.warning(f"Placeholders wasn't parsed successfully for '{manga.name}'")
            MM.show_message('warning', f"Placeholders wasn't parsed successfully for '{manga.name}'")
            return
            
        logger.success(f"Got placeholders for '{manga.name}' chapter {chapter.number}")
        chapter.add_images([ChapterImage(number=num, width=placeholder[0], height=placeholder[1]) for num, placeholder in enumerate(placeholders)])
        return placeholders

    def get_manga_from_url(self, url):
        url_parser = UrlParser(url)
        site = url_parser.site
        _id = url_parser.manga_id
        name = _id.title().replace('-', ' ')

        if not os.path.exists(f'{MANGA_DIR}/{_id}'):
            os.makedirs(f'{MANGA_DIR}/{_id}')
            
        cover = self.ensure_cover(_id, url_parser)

        return Manga(name, _id, cover, [site.name])
    
    def ensure_cover(self, manga: Manga):
        if os.path.exists(f'{manga.folder}/cover.jpg'):
            return 'cover.jpg'
        
        if manga.id_dex:
            cover = self.dex_scraper.get_manga_cover(manga.id_dex)
        elif manga.backup_sites:
            scraper = MangaSiteScraper(self.sites_manager, sites=manga.backup_sites)
            cover = scraper.get_manga_cover(manga)  # TODO
        else:
            MM.show_message('error', f"No available site for {manga.id_} was found")
            return None
        
        if cover:    
            with open(f'{manga.folder}/cover.jpg', 'wb') as f:
                f.write(cover)

            return 'cover.jpg'
        return None
    
    def add_chapter(self, manga: Manga, chapter: MangaChapter):
        manga.add_chapter(chapter)
        
    def save(self):
        self.repository.save(self.manga_collection)