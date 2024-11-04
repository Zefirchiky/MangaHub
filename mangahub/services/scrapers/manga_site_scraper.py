import requests # type: ignore
import io
import os

from bs4 import BeautifulSoup
from PIL import Image

from services.parsers import SitesJsonParser, UrlParser
from models import Manga
from gui.gui_utils import MM
from utils import BatchWorker, get_webp_dimensions


class MangaSiteScraper:
    def __init__(self, sites_parser: SitesJsonParser):
        self.sites_parser = sites_parser
        self.chapter_pages = {}

    def get_title_page(self) -> requests.Response | BeautifulSoup:
        if self.manga:
            for _site in self.manga.sites:
                self.site = self.sites_parser.get_site(_site)
                url = self.sites_parser.get_title_page_url(self.site, self.manga)

                return self.get_bs_from_url(url)

            MM.show_message('error', f"No site for the {self.manga.name} available")
            raise Exception(f"No site for the {self.manga.name} available")
        
        elif self.url_parser:                
            return self.get_bs_from_url(self.url_parser.url)

        MM.show_message('error', "Manga or url not found")
        raise Exception("Manga or url not found")      
    
    def get_manga_cover(self) -> bytes:
        if not self.title_page:
            self.title_page = self.get_title_page()
    
        cover = self.title_page.find('img', class_=self.site.title_page['cover_html_class'])
        img_data = requests.get(cover.get('src')).content

        return img_data
    
    def save_manga_cover_path(self, path, file='cover.jpg') -> str:
        file_path = os.path.join(path, file)
        
        image = self.get_manga_cover()

        with open(file_path, 'wb') as f:
            f.write(image)

        return file_path

    def get_chapter_page(self, manga: Manga, num) -> BeautifulSoup | None:
        if manga.name in self.chapter_pages:
            if num in self.chapter_pages[manga.name]:
                return self.chapter_pages[manga.name][num]
            
        if not manga.sites:
            MM.show_message('error', f"No sites for {manga.name} {num} was found")
            return None
        
        for _site in manga.sites:
            self.site = self.sites_parser.get_site(_site)
            url = UrlParser.get_chapter_page_url(self.site, manga, num)

            soup = self.get_bs_from_url(url)
            if soup:
                if not manga.name in self.chapter_pages:
                    self.chapter_pages[manga.name] = {}
                self.chapter_pages[manga.name][num] = soup
                MM.show_message('success', f"Chapter {manga.name} {num} page loaded")
                return soup
            
        MM.show_message('error', f"Chapter {manga.name} {num}: No site responded")
        return None
    
    def get_chapter_name(self, manga: Manga, num) -> str:
        chapter_page = self.get_chapter_page(manga, num)
        
        if not chapter_page:
            return None
        
        name = chapter_page.find('h2', class_=self.site.chapter_page['title_html_class'])
        return name.text if name else ''
    
    def get_chapter_image_urls(self, manga: Manga, num) -> list[str]:
        chapter_page = self.get_chapter_page(manga, num)
        
        if not chapter_page:
            return None
        
        urls = [img.get('src') for img in chapter_page.find_all('img', class_=self.site.chapter_page['images_html_class'])]
        return urls
    
    def get_image_size(self, url):
        headers = {"Range": "bytes=0-1023"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        if response.headers["Content-Type"] == "image/webp":
            return get_webp_dimensions(response.content)
        
        image = Image.open(io.BytesIO(response.content))
        return image.size
    
    def get_chapter_placeholders(self, manga: Manga, num) -> bytes:
        image_urls = self.get_chapter_image_urls(manga, num)
        if not image_urls:
            return 
        
        placeholders_worker = BatchWorker()
        placeholders_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Image sizes downloaded"))
        placeholders_worker.signals.error.connect(lambda error: MM.show_message('error', str(error), 5000))
        placeholders = list(placeholders_worker.process_batch(self.get_image_size, image_urls, blocking=True))
        return placeholders
    
    def start_chapter_images_download(self, manga: Manga, num):
        image_urls = self.get_chapter_image_urls(manga, num)
        if not image_urls:
            return 
        
        images_worker = BatchWorker()
        images_worker.signals.all_completed.connect(lambda _: MM.show_message('success', "Images downloaded"))
        images_worker.process_batch(requests.get, image_urls, blocking=False)
        return images_worker

    def get_bs_from_url(self, url) -> BeautifulSoup:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            MM.show_message('error', str(e), 5000)
            raise Exception(e)
        return BeautifulSoup(response.text, 'html.parser')
