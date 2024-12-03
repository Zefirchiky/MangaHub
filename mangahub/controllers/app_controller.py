from PySide6.QtCore import QObject, Signal
from loguru import logger

from .manga_manager import MangaManager, SitesManager
from services.parsers import StateParser
from models import MangaState, Manga, MangaChapter


class AppController:
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.sites_manager: SitesManager = app.sites_manager
        self.manga_manager: MangaManager = app.manga_manager
        self.manga_state = MangaState()
        
        self.manager = None
        self.state = None
                
        logger.success('AppController initialized')
        
    def init_connections(self):
        self.manga_changed = self.manga_state._signals.manga_changed
        self.chapter_changed = self.manga_state._signals.chapter_changed
        self.manga_state._signals.chapter_num_changed.connect(self.set_chapter)
                
        logger.success('AppController connections initialized')
        
    def get_manga_chapter_placeholders(self):
        return self.manga_manager.get_chapter_placeholders(self.manga_state._manga, self.manga_state._chapter)
                
    def select_manga_chapter(self, name: str, chapter: int | float) -> None:
        self.select_manga(name)
        self.select_chapter(chapter)
        
    def select_manga(self, name: str) -> None:
        self.manager = self.manga_manager
        self.state = self.manga_state
        
        manga = self.manager.get_manga(name)
        self.manga_state.set_manga(manga, 1)
        
    def select_chapter(self, number: int | float) -> None:
        if self.state._manga:
            self.state.set_chapter_num(number)
            
    def set_chapter(self, number: float):
        chapter = self.manager.get_chapter(self.state._manga, number)
        self.state.set_chapter(chapter)
            
    def select_next_chapter(self) -> None:
        self.state.next_chapter()
            
    def select_prev_chapter(self) -> None:
        self.state.prev_chapter()
            
    def save(self) -> None:
        self.manga_manager.save()
        self.sites_manager.save()
        StateParser('manga_state.json', MangaState).save(self.manga_state)
        