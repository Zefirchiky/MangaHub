from pydantic import field_validator
from ..tags.tag_model import TagModel
from ..manga.image_parsing_method import ImageParsingMethod
from ..manga.manga import Manga
from .site_chapter_page import SiteChapterPage
from .site_title_page import SiteTitlePage
from ..url import URL


class Site(TagModel):
    name: str
    url: str | URL
    language: str = 'en'
    title_page: SiteTitlePage = SiteTitlePage()
    chapter_page: SiteChapterPage
    images_parsing: ImageParsingMethod
    manga: dict[str, dict[str, str]] = {}
    
    @field_validator('url')
    def validate_url(cls, url: str | URL) -> URL:
        if isinstance(url, str):
            url = URL(url=url)
        return url
    
    def add_manga(self, manga: Manga, num_identifier: str = '') -> None:
        self.manga[manga.name] = {'id': manga.id_}
        if num_identifier:
            self.manga[manga.name]['num_identifier'] = num_identifier
        self.manga = self.manga
        
    def get_manga_identifier(self, manga_name: str) -> str:
        return self.manga.get(manga_name, {}).get('num_identifier')