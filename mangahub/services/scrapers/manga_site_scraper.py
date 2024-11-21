import requests # type: ignore
import io
import os

from bs4 import BeautifulSoup
from PIL import Image
from loguru import logger

from services.parsers import SitesParser, UrlParser
from models import Manga, Site
from gui.gui_utils import MM
from utils import BatchWorker, get_webp_dimensions


class MangaSiteScraper:
    def __init__(self, sites_parser: SitesParser):
        self.sites_parser = sites_parser
        self.title_pages = {}
        self.chapter_pages = {}
        
        logger.success('MangaSiteScraper initialized')

    def get_title_page(self, manga: Manga) -> BeautifulSoup:
        if manga.name in self.title_pages:
            return self.title_pages[manga.name]

        if not manga.backup_sites:
            MM.show_message('error', f"No sites for '{manga.name}' was found")
            return None
        
        for _site in manga.backup_sites:
            self.site = self.sites_parser.get_site(_site)
            url = UrlParser.get_title_page_url(self.site, manga)

            title_page = self.get_bs_from_url(url)
            self.title_pages[manga.name] = title_page
            return title_page
    
    def get_manga_cover(self) -> bytes: # TODO
        title_page: BeautifulSoup = self.get_title_page()
    
        cover = title_page.find('img', class_=self.site.title_page['cover_html_class'])
        if not cover:
            return None
        
        img_data = requests.get(cover.get('src')).content
        return img_data

    def get_chapter_page(self, site: Site, manga: Manga, num) -> BeautifulSoup | None:
        if manga.name in self.chapter_pages:
            if num in self.chapter_pages[manga.name]:
                return self.chapter_pages[manga.name][num]

        url = UrlParser.get_chapter_page_url(site, manga, num)
        print(url)

        soup = self.get_bs_from_url(url)
        if soup:
            if not manga.name in self.chapter_pages:
                self.chapter_pages[manga.name] = {}
            self.chapter_pages[manga.name][num] = soup
            MM.show_message('success', f"Chapter '{manga.name}' {num} page loaded")
            return soup
            
        MM.show_message('error', f"Chapter '{manga.name}' {num}: No site responded")
        return None
    
    def get_chapter_name(self, manga: Manga, num) -> str:
        chapter_page = self.get_chapter_page(manga, num)
        
        if not chapter_page:
            return None
        
        name = chapter_page.find('h2', class_=self.site.chapter_page['title_html_class'])
        return name.text if name else ''
    
    def get_chapter_image_urls(self, site: Site, manga: Manga, num) -> list[str]:
        chapter_page = self.get_chapter_page(site, manga, num)
        
        if not chapter_page:
            logger.warning(f"No chapter page for '{manga.name}' chapter {num} with site '{site.name}'")
            return None
        
        urls = [img.get('src') for img in chapter_page.find_all('img', class_=site.chapter_page['images_html_class'])]
        return urls
    
    def get_image_size(self, url):
        headers = {"Range": "bytes=0-1023"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if response.headers["Content-Type"] == "image/webp":
            return get_webp_dimensions(response.content)
        
        image = Image.open(io.BytesIO(response.content))
        return image.size
    
    def get_chapter_placeholders(self, site: Site, manga: Manga, num: float) -> bytes:
        image_urls = self.get_chapter_image_urls(site, manga, num)
        if not image_urls:
            logger.warning(f"No image urls for '{manga.name}' chapter {num} with site '{site.name}'")
            return 
        
        placeholders_worker = BatchWorker()
        placeholders_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Image sizes downloaded"))
        placeholders_worker.signals.error.connect(lambda error: MM.show_message('error', str(error), 5000))
        placeholders_worker.signals.error.connect(logger.error)
        placeholders = list(placeholders_worker.process_batch(self.get_image_size, image_urls, blocking=True))
        return placeholders
    
    def get_chapter_images(self, site: Site, manga: Manga, num):
        image_urls = self.get_chapter_image_urls(site, manga, num)
        if not image_urls:
            return 
        
        images_worker = BatchWorker()
        images_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Images downloaded"))
        images_worker.process_batch(requests.get, image_urls, blocking=False)
        return images_worker

    def get_bs_from_url(self, url) -> BeautifulSoup:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.RequestException as e:
            MM.show_message('error', str(e), 5000)
            return None
        return BeautifulSoup(response.text, 'html.parser')
