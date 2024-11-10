from pydantic import BaseModel, PrivateAttr
from PySide6.QtCore import QObject, Signal
from models import Manga
from utils import BatchWorker


class MangaStateSignals(QObject):
    manga_changed = Signal(str)
    chapter_changed = Signal(int)

class MangaState(BaseModel):
    _manga: Manga | None = PrivateAttr(default=None)
    manga_name: str = ''
    chapter: int = 0
    _worker: BatchWorker | None = PrivateAttr(default=None)
    _signals: MangaStateSignals = PrivateAttr(default_factory=MangaStateSignals)
    
    def set_manga(self, manga: Manga, chapter: int):
        self._manga = manga
        self.manga_name = manga.name
        self.set_chapter(chapter, set_manga=True)
        self._signals.manga_changed.emit(manga)
        
    def set_chapter(self, chapter: int, set_manga=False):
        self.chapter = chapter
        self._manga.current_chapter = self.chapter
        self._manga.check_chapter(self.chapter)
        if not set_manga:
            self._signals.chapter_changed.emit(chapter)
        
    def set_worker(self, worker: BatchWorker):
        self._worker = worker
        
    def next_chapter(self):
        if not self.is_last():
            self.set_chapter(self.chapter + 1)
            
    def prev_chapter(self):
        if not self.is_first():
            self.set_chapter(self.chapter - 1)
            
    def is_first(self):
        return self.chapter <= 1        
    
    def is_last(self):
        return self.chapter >= self._manga.last_chapter