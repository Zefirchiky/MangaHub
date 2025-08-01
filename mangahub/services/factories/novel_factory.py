from controllers import SitesManager
from models import Url
from models.novels import Novel
from services.parsers import UrlParser


class NovelFactory:
    def __init__(self, sites_manager: SitesManager):
        self.sites_manager = sites_manager

    def create_novel(self, name: str) -> Novel:
        return Novel(name=name)

    def create_from_url(self, url: str | Url) -> Novel:
        url = Url(url)
        site = self.sites_manager.get(url=url)
        name = UrlParser(url).manga_id
        return Novel(
            name=name,
            site=site.name,
        )
