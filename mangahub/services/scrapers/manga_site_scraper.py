from bs4 import BeautifulSoup

from gui.gui_utils import MM
from services.parsers import SitesJsonParser, UrlParser
from models import Manga

import requests # type: ignore
import os


class MangaSiteScraper:
    def __init__(self, sites_parser: SitesJsonParser, manga: Manga=None, url_parser: UrlParser=None):
        self.sites_parser = sites_parser
        self.manga = manga
        self.url_parser = url_parser
        
        self.title_page = None
        self.chapter_page = None

        if self.url_parser:
            self.site = self.url_parser.get_site()
            if not self.site:
                MM.show_message('error', "Site not found")
                raise Exception("Site not found")

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

    def get_chapter_page(self, num) -> BeautifulSoup | None:
        if self.manga:
            for _site in self.manga.sites:
                self.site = self.sites_parser.get_site(_site)
                print(self.manga)
                url = UrlParser.get_chapter_page_url(self.site, self.manga, num)

                return self.get_bs_from_url(url)
            
            MM.show_message('error', f"No site for the {self.manga.name} available")
            raise Exception(f"No site for the {self.manga.name} available")
            
        MM.show_message('error', "No manga found")
        raise Exception("No manga found")
    
    def get_chapter_name(self, num) -> str:
        if not self.chapter_page:
            self.chapter_page = self.get_chapter_page(num)

        return self.chapter_page.find('h2', class_=self.site.chapter_page['title_html_class']).text
    
    def get_chapter_images(self, num) -> bytes:
        if not self.chapter_page:
            self.chapter_page = self.get_chapter_page(num)

        images = []
        for image in self.chapter_page.find_all('img', class_=self.site.chapter_page['images_html_class']):
            img_content = requests.get(image.get('src')).content
            images.append(img_content)

        return images

    def get_bs_from_url(self, url) -> BeautifulSoup:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            MM.show_message('error', str(e), 5000)
            raise Exception(e)
        return BeautifulSoup(response.text, 'html.parser')
