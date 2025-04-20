from typing import TYPE_CHECKING

from loguru import logger
from models.novels import Novel, NovelChapter
from services.repositories import NovelsRepository
from services.scrapers import NovelsSiteScraper
from utils import MM

if TYPE_CHECKING:
    from mangahub.main import App


class NovelsManager:
    def __init__(self, app: 'App'):
        self.app = app
        self.repository: NovelsRepository = self.app.novels_repository
        self.repository.load()
        self.scraper = NovelsSiteScraper(self.app.sites_manager)
        self.sites_manager = self.app.sites_manager
        
        logger.success('NovelsManager initialized')
        
    def get_novel(self, name: str) -> Novel:
        novel = self.repository.get(name)
        if not novel:
            MM.show_warning(f"Novel {name} not found")
        
        return self._ensure_novels_essential_data({novel.name: novel})
    
    def get_all_novels(self) -> dict[str, Novel]:
        return self._ensure_novels_essential_data(self.repository.get_all())
    
    def get_chapter(self, novel: Novel, num: float | int) -> NovelChapter | None:
        return novel._chapters_data.get(num)
    
    
    def create_novel(self, name: str) -> Novel:
        novel = Novel(
            name=name,
            
        )
        
    def create_novel_from_text(self, text: str):
        text = self.scraper.get_temp_novel_text()
        
    
    
    @classmethod
    def _ensure_novels_essential_data(cls, novels: dict[str, Novel]) -> dict[str, Novel]:
        for novel in novels.values():
            if not novel._chapters_data.get(1):
                novel.add_chapter(cls.get_chapter(novel, 1))
            if not novel._chapters_data.get(novel.last_chapter):
                novel.add_chapter(cls.get_chapter(novel, novel.last_chapter))
            if novel.current_chapter != 1 and novel.current_chapter != novel.last_chapter and \
                novel.current_chapter and not novel._chapters_data.get(novel.current_chapter):
                novel.add_chapter(cls.get_chapter(novel, novel.current_chapter))
            
        return novels