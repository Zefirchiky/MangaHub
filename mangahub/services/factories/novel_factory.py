from controllers import SitesManager
from models import URL
from models.novels import Novel
from services.parsers import UrlParser


class NovelFactory:
    def __init__(self, sites_manager: SitesManager):
        self.sites_manager = sites_manager
        
    def create_novel(self, name: str) -> Novel:
        return Novel(name=name)
    
    def create_from_url(self, url: str | URL) -> Novel:
        url = URL(url)
        site = self.sites_manager.get_site(url=url)
        name = UrlParser(url).manga_name
        return Novel(
            name=name,
            site=site.name,
        )