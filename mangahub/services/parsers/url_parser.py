import re
from services.parsers import SitesJsonParser
from models import Site, Manga
from gui.gui_utils import MM


class UrlParser:
    def __init__(self, url: str, parser: SitesJsonParser):
        self.url = url
        self.parser = parser

        self.site = None
        self.site = self.get_site()
        self.regex_match = self.get_regex_match()

    def get_site(self):
        if self.site:
            return self.site
        
        for site in self.parser.get_all_sites().values():
            if site.url in self.url:
                return site

        MM.show_message('error', f"No site for {self.url} was found")
        return None

    def get_regex_match(self):
        url_pattern = self.site.url + "/" + self.site.title_page['url_format'].replace(
            '$manga_id$', r'(?P<manga_id>[a-zA-Z0-9\-]+)'
        ).replace(
            '$num_identifier$', r'(?P<num_identifier>[a-zA-Z0-9]+)'
        )

        regex = re.compile(url_pattern)
        
        return regex.match(self.url)

    def get_manga_id(self):
        return self.regex_match.group('manga_id')
    
    def get_num_identifier(self):
        return self.regex_match.group('num_identifier')
    
    @staticmethod
    def get_title_page_url(site: Site, manga_id, manga_name) -> str:
        url = site.url + "/" + site.title_page['url_format'].replace(
                '$manga_id$', manga_id
            ).replace(
                '$num_identifier$', site.manga[manga_name]['num_identifier']
            )

        return url

    @staticmethod
    def get_chapter_page_url(site: Site, manga_id, manga_name, chapter_num: int) -> str:
        url = site.url + "/" + site.chapter_page['url_format'].replace(
                '$manga_id$', manga_id
            ).replace(
                '$num_identifier$', site.manga[manga_name]['num_identifier']
            ).replace(
                '$chapter_num$', str(chapter_num)
            )

        return url


