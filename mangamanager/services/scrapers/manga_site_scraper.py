from PySide6.QtGui import QImage, QPixmap
from services.parsers import SitesJsonParser
from models import Site, Manga
from bs4 import BeautifulSoup
import requests # type: ignore
import os
import re


class MangaSiteScraper:
    sites_parser = SitesJsonParser()

    def __init__(self, manga: Manga=None, url: str=None, sites_parser: SitesJsonParser=sites_parser):
        self.manga = manga
        self.url = url
        
        self.sites_parser = sites_parser
        self.title_page = None
        self.chapter_page = None

        if self.url:
            self.site = get_site_from_url(self.sites_parser, self.url)
            if not self.site:
                raise Exception("Site not found")

    def get_title_page(self) -> requests.Response | BeautifulSoup:
        if self.manga:
            for _site in self.manga.sites:
                self.site = self.sites_parser.get_site(_site)
                url = self.sites_parser.get_title_page_url(self.site, self.manga)

                return self.get_bs_from_url(url)

            raise Exception(f"No site for the {self.manga.name} available")
        
        elif self.url:                
            return self.get_bs_from_url(self.url)

        raise Exception("Manga or url not found")      
    
    def get_manga_cover(self):
        if not self.title_page:
            self.title_page = self.get_title_page()
    
        cover = self.title_page.find('img', class_=self.site.title_page['cover_html_class'])
        img_data = requests.get(cover.get('src')).content

        return img_data
    
    def save_manga_cover_path(self, path, file='cover.jpg'):
        file_path = os.path.join(path, file)
        file = 'cover.jpg'
        
        image = self.get_manga_cover()

        with open(file_path, 'wb') as f:
            f.write(image)

        return file_path

    def get_chapter_page(self, num) -> BeautifulSoup | None:
        if self.manga:
            for _site in self.manga.sites:
                self.site = self.sites_parser.get_site(_site)
                url = self.sites_parser.get_chapter_page_url(self.site, self.manga, num)

                return self.get_bs_from_url(url)

            return None
        
        elif self.url:                
            return self.get_bs_from_url(self.url)
        
        return None
    
    def get_chapter_name(self, num) -> str:
        if not self.chapter_page:
            self.chapter_page = self.get_chapter_page(num)

        return self.chapter_page.find('h2', class_=self.site.chapter_page['chapter_html_class']).text
    
    def get_chapter_image_iter(self, num) -> bytes:
        if not self.chapter_page:
            self.chapter_page = self.get_chapter_page(num)

        for image in self.chapter_page.find_all('img', class_=self.site.chapter_page['images_html_class']):
            return requests.get(image.get('src')).content

        return None
    
    def get_bs_from_url(self, url) -> BeautifulSoup:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise Exception(e)
        return BeautifulSoup(response.text, 'html.parser')
    

def get_site_from_url(parser: SitesJsonParser, url: str):
    for site in parser.get_all_sites():
        if site.url in url:
            return site

    print("Site not found")
    return None

def get_name_identifier_from_url(site: Site, url: str):
    url_pattern = site.url + "/" + site.title_page['url_format'].replace(
        '$manga_id$', r'(?P<manga_id>[a-zA-Z0-9\-]+)'
    ).replace(
        '$num_identifier$', r'(?P<num_identifier>[a-zA-Z0-9]+)'
    )

    regex = re.compile(url_pattern)
    
    match = regex.match(url)
    
    if match:
        return match.group('manga_id'), match.group('num_identifier')
    
    return None, None
    