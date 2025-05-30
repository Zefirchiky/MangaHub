from models.manga import Manga, MangaChapter
from pydantic import BaseModel, PrivateAttr
from PySide6.QtCore import QObject, Signal
from utils import BatchWorker


class MangaStateSignals(QObject):
    manga_changed = Signal(Manga)
    chapter_changed = Signal(MangaChapter)
    chapter_num_changed = Signal(int)


class MangaState(BaseModel):
    manga_id: str = ""
    chapter_num: float = 0

    _manga: Manga = PrivateAttr(default=None)
    _chapter: MangaChapter = PrivateAttr(default=None)
    _worker: BatchWorker | None = PrivateAttr(default=None)
    _signals: MangaStateSignals = PrivateAttr(default_factory=MangaStateSignals)

    def get_media(self) -> Manga:
        return self._manga
        
    def set_manga(self, manga: Manga):
        self._manga = manga
        self.manga_id = manga.id_
        self._signals.manga_changed.emit(manga)

    def set_chapter(self, chapter: float):
        self.chapter_num = chapter
        self._chapter = self._manga.get_chapter(chapter)
        self._signals.chapter_changed.emit(self._chapter)

    def set_chapter_num(self, chapter_num: int | float):
        self.chapter_num = chapter_num
        self._signals.chapter_num_changed.emit(chapter_num)

    def set_worker(self, worker: BatchWorker):
        self._worker = worker

    def is_first(self):
        return self.chapter_num <= 1

    def is_last(self):
        return self.chapter_num >= self._manga.last_chapter
