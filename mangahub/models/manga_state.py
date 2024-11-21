from pydantic import BaseModel, PrivateAttr
from PySide6.QtCore import QObject, Signal
from models import Manga, MangaChapter
from utils import BatchWorker


class MangaStateSignals(QObject):
    manga_changed = Signal(str)
    chapter_changed = Signal(int)

class MangaState(BaseModel):
    _manga: Manga | None = PrivateAttr(default=None)
    manga_name: str = ''
    _chapter: MangaChapter | None = PrivateAttr(default=None)
    chapter_num: int | float = 0
    _worker: BatchWorker | None = PrivateAttr(default=None)
    _signals: MangaStateSignals = PrivateAttr(default_factory=MangaStateSignals)
    
    def set_manga(self, manga: Manga, chapter: int):
        self._manga = manga
        self.manga_name = manga.name
        self.chapter_num = chapter
        self._signals.manga_changed.emit(manga)
        
    def set_chapter(self, chapter: MangaChapter):
        self._chapter = chapter
        self.set_chapter_num(chapter.number)
        
    def set_chapter_num(self, chapter_num: int):
        self.chapter_num = chapter_num
        self._manga.current_chapter = self.chapter_num
        self._manga.check_chapter(self.chapter_num)
        self._signals.chapter_changed.emit(self._chapter)
        
    def set_worker(self, worker: BatchWorker):
        self._worker = worker
        
    def next_chapter(self):
        if not self.is_last():
            self.set_chapter_num(self.chapter_num + 1)
            
    def prev_chapter(self):
        if not self.is_first():
            self.set_chapter_num(self.chapter_num - 1)
            
    def is_first(self):
        return self.chapter_num <= 1        
    
    def is_last(self):
        return self.chapter_num >= self._manga.last_chapter