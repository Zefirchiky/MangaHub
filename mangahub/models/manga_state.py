from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal
from models import Manga
from utils import BatchWorker


class MangaStateSignals(QObject):
    manga_changed = Signal(str)
    chapter_changed = Signal(int)

@dataclass
class MangaState:
    manga: Manga = None
    chapter: int = 0
    worker: BatchWorker = None
    signals: MangaStateSignals = MangaStateSignals()
    
    def set_manga(self, manga: Manga, chapter: int):
        self.manga = manga
        self.chapter = chapter
        self.signals.manga_changed.emit(manga)
        
    def set_chapter(self, chapter: int):
        self.chapter = chapter
        self.manga.current_chapter = self.chapter
        self.signals.chapter_changed.emit(chapter)
        
    def set_worker(self, worker: BatchWorker):
        self.worker = worker
        
    def next_chapter(self):
        if not self.is_last():
            self.chapter += 1
            self.manga.current_chapter = self.chapter
            self.signals.chapter_changed.emit(self.chapter)
            
    def prev_chapter(self):
        if not self.is_first():
            self.chapter -= 1
            self.manga.current_chapter = self.chapter
            self.signals.chapter_changed.emit(self.chapter)
            
    def is_first(self):
        return self.chapter <= 1        
    
    def is_last(self):
        return self.chapter >= self.manga.last_chapter
    
    def as_dict(self):
        return {
            "manga": self.manga.name,
            "chapter": self.chapter
        }