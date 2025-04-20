import io
import re

import requests
from bs4 import BeautifulSoup
from loguru import logger
from models.manga import Manga
from models.sites import Site
from PIL import Image
from services.parsers import UrlParser
from utils import MM, BatchWorker
from utils.image_dimensions import get_dimensions_from_bytes

# TODO: reimplement


class MangaSiteScraper:
    def __init__(self, sites_manager):
        self.sites_manager = sites_manager
        self.title_pages = {}
        self.chapter_pages = {}
        
        logger.success('MangaSiteScraper initialized')

    def get_title_page(self, site: Site, manga: Manga) -> BeautifulSoup:
        if manga.name in self.title_pages:
            return self.title_pages[manga.name]

        url = UrlParser.get_title_page_url(site, manga)

        title_page = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0'}).text
        self.title_pages[manga.name] = title_page
        return title_page
    
    def get_manga_cover(self) -> bytes: # TODO
        title_page: BeautifulSoup = self.get_title_page()
    
        cover = title_page.find('img', class_=self.site.title_page['cover_html_class'])
        if not cover:
            return None
        
        img_data = requests.get(cover.get('src')).content
        return img_data
    
    def get_last_chapter_num(self, site: Site, manga: Manga) -> int:
        if site.last_chapter_parsing.on_title_page:
            html = self.get_title_page(site, manga)
        elif site.last_chapter_parsing.on_chapter_page:
            html = self.get_chapter_page(site, manga, site.last_chapter_parsing.on_chapter_page).text
        
        regex_url = site.last_chapter_parsing.string_format.replace(
                '$chapter_num$', r'(?P<chapter_num>[0-9]+)'
            ).replace(
                '$manga_id$', manga.id_
            ).replace(
                '$num_identifier$', r'\w+'
            )   # TODO
            
        regex = re.compile(regex_url)
        chapter_nums = regex.findall(html)
        if not chapter_nums:
            logger.warning(f"No match for {regex_url} ({site.last_chapter_parsing.string_format}) was found")
            return 0
        
        return max([int(i) for i in chapter_nums])

    def get_chapter_page(self, site: Site, manga: Manga, num) -> BeautifulSoup | None:
        if manga.name in self.chapter_pages:
            if num in self.chapter_pages[manga.name]:
                return self.chapter_pages[manga.name][num]

        url = UrlParser.get_chapter_page_url(site, manga, num)

        chapter_page = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0'}).text
        if chapter_page:
            if manga.name not in self.chapter_pages:
                self.chapter_pages[manga.name] = {}
            self.chapter_pages[manga.name][num] = chapter_page
            MM.show_success(f"Chapter '{manga.name}' {num} page loaded")
            return chapter_page
            
        MM.show_error(f"Chapter '{manga.name}' {num}: No site responded")
        return None
    
    def get_chapter_name(self, site: Site, manga: Manga, num) -> str:
        chapter_page = BeautifulSoup(self.get_chapter_page(site, manga, num), 'html.parser')
        
        if not chapter_page:
            return None
        
        name = chapter_page.find('h2', class_=site.chapter_page.title_class)
        return name.text if name else ''
    
    def get_chapter_image_urls(self, site: Site, manga: Manga, num) -> list[str]:
        chapter_page = BeautifulSoup(self.get_chapter_page(site, manga, num), 'html.parser')
        
        if not chapter_page:
            logger.warning(f"No chapter page for '{manga.name}' chapter {num} with site '{site.name}'")
            return None
        
        if not site.images_parsing.is_set:
            logger.warning(f"No images_parsing is set for '{site.name}'")
            return None
        
        if site.images_parsing.regex_from_html:
            scripts: list[BeautifulSoup] = chapter_page.find_all('script')
            for script in scripts:
                if script.string:
                    urls = re.findall(re.compile(site.images_parsing.url_regex), script.string)
                    if urls:
                        return urls
        
        elif site.images_parsing.bs_from_loaded_html:
            urls = [img.get('src') for img in chapter_page.find_all(
                'img', 
                class_=site.images_parsing.class_,
                id_=site.images_parsing.id_format,
                alt_=site.images_parsing.alts_format
                )]
            return urls
        
        logger.warning(f"No image urls for '{manga.name}' chapter {num} with site '{site.name}'")
        return None
    
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
        placeholders_worker.signals.all_completed.connect(lambda _: MM.show_success("Image sizes downloaded"))
        placeholders_worker.signals.error.connect(lambda error: MM.show_error(str(error), 5000))
        placeholders = list(placeholders_worker.process_batch(self.get_image_size, image_urls, blocking=True))
        return placeholders
    
    def get_chapter_images(self, site: Site, manga: Manga, num):
        image_urls = self.get_chapter_image_urls(site, manga, num)
        if not image_urls:
            return 
        
        images_worker = BatchWorker()
        images_worker.signals.all_completed.connect(lambda _: MM.show_success("Images downloaded"))
        images_worker.process_batch(requests.get, image_urls, blocking=False)
        return images_worker

    def get_bs_from_url(self, url) -> BeautifulSoup:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.RequestException as e:
            MM.show_error(str(e), 5000)
            return None
        return BeautifulSoup(response.text, 'html.parser')
