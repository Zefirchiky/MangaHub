from abc import ABC

from pydantic import PrivateAttr
from PySide6.QtCore import Signal, QObject

from ..tags.tag_model import TagModel


class ChapterNotFoundError(Exception):
    pass


class AbstractChapterSignals(QObject):
    is_read_changed = Signal(bool)


class AbstractChapter(ABC, TagModel):
    number: int | float
    name: str = ""
    upload_date: str = ""
    translator: str = ""
    language: str = "en"

    is_read: bool = False

    _signals: AbstractChapterSignals = PrivateAttr(
        default_factory=AbstractChapterSignals
    )

    def set_is_read(self, is_read: bool = True):
        self.is_read = is_read
        self._signals.is_read_changed.emit(self.is_read)

    def __str__(self) -> str:
        return f"Chapter {self.number}{f': {self.name}' if self.name else ''}"
