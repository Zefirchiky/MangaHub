from loguru import logger

from services.parsers import SitesParser
from models import Site, SiteChapterPage, ImageParsingMethod


class SitesManager:
    def __init__(self, app):
        self.app = app
        self.parser: SitesParser = app.sites_json_parser
        self.sites = self.parser.get_all_sites()
        
        logger.success('SitesManager initialized')
        
    def create_site(self, name: str, url: str, chapter_page: SiteChapterPage, image_parsing: ImageParsingMethod, **kwargs) -> Site:
        site = Site(name=name, url=url, chapter_page=chapter_page, images_parsing=image_parsing, **kwargs)
        self.sites[name] = site
        return site
        
    def get_all_sites(self):
        return self.sites
    
    def get_site(self, name):
        return self.parser.get_site(name)
    
    def save(self):
        self.parser.save(self.sites)