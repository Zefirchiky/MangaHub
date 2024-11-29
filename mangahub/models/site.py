from .tags.tag_model import TagModel
from pydantic import HttpUrl
from .image_parsing_method import ImageParsingMethod
from .site_chapter_page import SiteChapterPage
from .site_title_page import SiteTitlePage


class Site(TagModel):
    name: str
    url: str
    language: str = 'en'
    title_page: SiteTitlePage = SiteTitlePage()
    chapter_page: SiteChapterPage
    images_parsing: ImageParsingMethod
    manga: dict[str, dict[str, str]] = {}
    
    def add_manga(self, manga_name: str, num_identifier: str = '') -> None:
        self.manga[manga_name] = {
            'name': manga_name,
            'num_identifier': num_identifier
        }
        
    def get_manga_identifier(self, manga_name: str) -> str:
        return self.manga.get(manga_name, {}).get('num_identifier')
