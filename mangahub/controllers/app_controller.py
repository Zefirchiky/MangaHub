from loguru import logger
from models import URL
from models.manga import Manga, MangaState
from services.parsers import StateParser

from .manga_manager import MangaManager, SitesManager
from models.abstract import ChapterNotFoundError


class AppController:
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.sites_manager: SitesManager = app.sites_manager
        self.manga_manager: MangaManager = app.manga_manager
        self.manga_state = MangaState()
        
        self.manager = None
        self.state = MangaState()
                
        logger.success('AppController initialized')
        
    def init_connections(self):
        self.manga_changed = self.state._signals.manga_changed
        self.chapter_changed = self.state._signals.chapter_changed
                
        logger.success('AppController connections initialized')
        
        
    def get_manga_chapter_placeholders(self):
        return self.manga_manager.get_chapter_placeholders(self.state._manga, self.state._chapter)
    
    def get_manga_chapter_images(self):
        return self.manga_manager.get_chapter_images(self.state._manga, self.state._chapter)
                
    
    def get_manga(self, name: str) -> Manga:
        return self.manga_manager.get_manga(name)
    
    def create_manga(self, name: str, url: str | URL='', site='MangaDex', backup_sites=[], **kwargs):
        manga = self.manga_manager.create_manga(name, url, site, backup_sites, **kwargs)
        return manga
    
    def remove_manga(self, name: str) -> Manga:
        return self.manga_manager.remove_manga(name)
        
                
    def select_media_chapter(self, name: str, chapter: int | float) -> None:
        self.select_manga(name)
        self.set_chapter(chapter)
        
    def select_manga(self, name: str) -> None:
        self.manager = self.manga_manager
        manga = self.manager.get_manga(name)
        self.state.set_manga(manga)
        
   
    def set_chapter(self, number: float):
        self.state.set_chapter_num(number)
        try:
            chapter = self.state._manga.get_chapter(self.state.chapter_num)
        except ChapterNotFoundError:
            chapter = self.manager.get_chapter(self.state._manga, self.state.chapter_num)
        self.state.set_chapter(chapter)
            
    def next_chapter(self) -> None:
        if not self.state.is_last():
            self.set_chapter(self.state.chapter_num + 1)
            
    def prev_chapter(self) -> None:
        if not self.state.is_first():
            self.set_chapter(self.state.chapter_num - 1)
            
    def save(self) -> None:
        self.manga_manager.save()
        self.sites_manager.save()
        StateParser('manga_state.json', MangaState).save(self.state)
        