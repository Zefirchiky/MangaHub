from __future__ import annotations

from loguru import logger
from PySide6.QtCore import QObject, Signal, QTimer

from models import Url
from models.images import ImageMetadata
from models.sites import Site
from models.manga import MangaState, MangaChapter
from services.repositories import StateRepository

from .manga_manager import MangaManager
from .sites_manager import SitesManager
from models.manga import Manga
from config import Config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class MangaSignals(QObject):
    chapter_started_loading = Signal(str, MangaChapter) # manga.id_
    image_meta_loaded = Signal(int, ImageMetadata)      # i, metadata
    image_loaded = Signal(int, ImageMetadata)                     # i, name
    sites_checked = Signal(str, list)

class AppController(QObject):
    manga_signals = MangaSignals()
    manga_created = Signal(Manga)
    
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self.sites_manager: SitesManager = app.sites_manager
        self.manga_manager: MangaManager = app.manga_manager
        self.manga_state = MangaState()

        self.manager = self.manga_manager  # TODO
        self.state = MangaState()
        
        self.chapter_load_timer = QTimer()

        logger.success("AppController initialized")

    def init_connections(self):
        self.manga_changed = self.state._signals.manga_changed
        self.chapter_changed = self.state._signals.chapter_changed
        
        self.sites_manager.manga_signals.sites_checked.connect(self.manga_signals.sites_checked.emit)
        
        self.manga_manager.image_meta_loaded.connect(self.manga_signals.image_meta_loaded.emit)
        self.manga_manager.image_loaded.connect(self.manga_signals.image_loaded.emit)

        logger.success("AppController connections initialized")

    def get_manga(self, name: str) -> Manga | None:
        return self.manga_manager.get(name)

    def find_manga_sites(self, name: str):
        if Url.is_url(name):
            self.manga_signals.sites_checked.emit(name, [self.sites_manager.get_site_from_url(Url(name)).name])
        else:
            self.sites_manager.find_media_sites(MangaManager.get_id_from_name(name))

    def create_manga(
        self, name: str, url: str | Url = "", site="MangaDex", sites=[], overwrite=False, **kwargs
    ):
        manga = self.manga_manager.create(name, site, overwrite=overwrite, **kwargs)
        self.manga_created.emit(manga)
        return manga

    def remove_manga(self, name: str) -> Manga:
        return self.manga_manager.remove(name)

    def select_media_chapter(self, name: str, chapter: float) -> None:
        self.select_manga(name)
        self.set_chapter(chapter)

    def select_manga(self, name: str) -> None:
        self.manager = self.manga_manager
        manga = self.manager.get(name)
        self.state.set_manga(manga)
    
    def set_chapter(self, number: float):
        self.chapter_load_timer.stop()
        self.chapter_load_timer.singleShot(Config.Downloading.Chapter.time_wait_before_loading(), lambda: self._set_chapter(number))
        
    def _set_chapter(self, number: float):
        media = self.state.get_media()
        media.set_changed()
        media.current_chapter = number
        if media.last_read_chapter not in media.checked_chapters:
            media.last_read_chapter = number
        self.state.set_chapter(number)
        self.state._chapter.set_is_read()
        self.load_chapter()
        
    def load_chapter(self):
        if isinstance(self.manager, MangaManager):
            self.manga_signals.chapter_started_loading.emit(self.state.get_media(), self.state._chapter)
        self.manager.load_chapter(self.state.get_media(), self.state.chapter_num)
        

    def next_chapter(self) -> None:
        if not self.state.is_last():
            self.set_chapter(self.state.chapter_num + 1.)

    def prev_chapter(self) -> None:
        if not self.state.is_first():
            self.set_chapter(self.state.chapter_num - 1.)

    def save(self) -> None:
        self.manga_manager.save()
        self.sites_manager.save()
        StateRepository("manga_state.json", MangaState).save(self.state)
