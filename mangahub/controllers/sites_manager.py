from __future__ import annotations
from loguru import logger
from models import URL
from models.manga import ImageParsingMethod
from models.sites import Site, SiteChapterPage

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class SitesManager:
    def __init__(self, app: App):
        self.app = app
        self.repo = app.sites_repo

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
        ).set_changed()
        self.repo.add(name, site)
        return site

    def get_all(self) -> dict[str, Site]:
        return self.repo.get_all()

    def get(self, name: str = None, url: str | URL = None) -> Site | None:
        if url:
            url = URL(url)
            for site in self.repo.get_all().values():
                if site["url"] == url.site_url:
                    return site
        return self.repo.get(name)

    def save(self):
        self.repo.save()
