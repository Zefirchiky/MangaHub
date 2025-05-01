from loguru import logger
from models import URL
from models.manga import ImageParsingMethod
from models.sites import Site, SiteChapterPage
from services.parsers import SitesParser


class SitesManager:
    def __init__(self, app):
        self.app = app
        self.parser: SitesParser = app.sites_json_parser
        self.sites = self.parser.get_all_sites()

        logger.success("SitesManager initialized")

    def create_site(
        self,
        name: str,
        url: str,
        chapter_page: SiteChapterPage,
        image_parsing: ImageParsingMethod,
        last_chapter_parsing: ImageParsingMethod,
        **kwargs,
    ) -> Site:
        site = Site(
            name=name,
            url=url,
            chapter_page=chapter_page,
            images_parsing=image_parsing,
            last_chapter_parsing=last_chapter_parsing,
            **kwargs,
        )
        self.sites[name] = site
        return site

    def get_all_sites(self) -> dict[str, Site]:
        if self.sites:
            return self.sites
        return self.parser.get_all_sites()

    def get_site(self, name: str = None, url: str | URL = None) -> Site | None:
        if url:
            url = URL(url)
            for site in self.sites.values():
                if site["url"] == url.site_url:
                    return site
        return self.parser.get_site(name)

    def save(self):
        self.parser.save(self.sites)
