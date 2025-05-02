from __future__ import annotations
import re

from loguru import logger
from models import URL
from ..repositories.sites_repository import SitesRepository
from utils import MM

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.manga import Manga
    from models.sites import Site


class UrlParser:
    parser: SitesRepository

    def __init__(self, url: URL | str):
        if isinstance(url, str):
            url = URL(url)
        self.url = url

        self._cached_regex_match = None

    @classmethod
    def set_parser(cls, parser: SitesRepository):
        cls.parser = parser

    @property
    def site(self) -> Site | None:
        for site in self.parser.get_all().values():
            if site.url == self.url.site_url:
                return site

        MM.show_error(f"No site for {self.url} was found")
        return None

    @property
    def manga_name(self):
        for name, manga in self.site.manga.items():
            if manga["id"] == self.manga_id:
                return name

        logger.warning(
            f"No manga name for {self.url} was found, attempting to parse..."
        )
        return self.manga_id.replace("-", " ").title()

    @property
    def regex_match(self):
        if self._cached_regex_match:
            return self._cached_regex_match

        if self.site.title_page.url_format:
            format_ = self.site.title_page.url_format
        elif self.site.chapter_page.url_format:
            format_ = self.site.chapter_page.url_format
            logger.warning(
                f"No title page url format for {self.site.name} was found, attempting to parse with chapter page url format..."
            )

        url_pattern = (
            self.site.url.url
            + "/"
            + format_.replace("$manga_id$", r"(?P<manga_id>[a-zA-Z0-9\-]+)")
            .replace("$num_identifier$", r"(?P<num_identifier>[a-zA-Z0-9]+)")
            .replace("$chapter_num$", r"(?P<chapter_num>[0-9]+)")
            + r".*"
        )

        regex = re.compile(url_pattern)
        self._cached_regex_match = regex.match(self.url.url)
        if not self._cached_regex_match:
            MM.show_error(
                f"No match for {self.url} was found{' (try adding title page url format to the site)' if not self.site.title_page.url_format else ''}"
            )

        return self._cached_regex_match

    @property
    def manga_id(self):
        return self.regex_match.group("manga_id")

    @property
    def num_identifier(self):
        return self.regex_match.group("num_identifier")

    @staticmethod
    def get_title_page_url(site: Site, manga: Manga) -> str:
        url = (
            site.url.url
            + "/"
            + site.title_page.url_format.replace("$manga_id$", manga.id_)
        )

        num_identifier = site.manga.get(manga.name)
        if num_identifier:
            num_identifier = num_identifier.get("num_identifier")
        if not num_identifier:
            num_identifier = site.num_identifier
        if "$num_identifier$" in url and num_identifier:
            url = url.replace("$num_identifier$", num_identifier)

        return url

    @staticmethod
    def get_chapter_page_url(site: Site, manga: Manga, chapter_num: int) -> str:
        url = (
            site.url.url
            + "/"
            + site.chapter_page.url_format.replace("$manga_id$", manga.id_).replace(
                "$chapter_num$", str(chapter_num)
            )
        )

        num_identifier = site.manga.get(manga.name)
        if num_identifier:
            num_identifier = num_identifier.get("num_identifier")
        if not num_identifier:
            num_identifier = site.num_identifier
        if "$num_identifier$" in url and num_identifier:
            url = url.replace("$num_identifier$", num_identifier)

        return url
