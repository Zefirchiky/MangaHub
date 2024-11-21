from .tags.tag_model import TagModel

class Site(TagModel):
    name: str
    url: str
    language: str = 'en'
    title_page: dict[str, str] = {}
    chapter_page: dict[str, str] = {}
    manga: dict[str, dict[str, str]] = {}
    
    def add_manga(self, manga_name: str, num_identifier: str = None) -> None:
        self.manga[manga_name] = {
            'name': manga_name,
            'num_identifier': num_identifier
        }
        
    def get_manga_identifier(self, manga_name: str) -> str:
        return self.manga.get(manga_name, {}).get('num_identifier')
