from __future__ import annotations
from abc import ABC
from pathlib import Path

from pydantic import PrivateAttr
from PySide6.QtCore import Signal, QObject

from core.models.tags.tag_model import TagModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.repositories.abstract import ChapterDataRepository


class ChapterNotFoundError(Exception):
    pass


class AbstractChapterSignals(QObject):
    is_read_changed = Signal(bool)


class AbstractChapter[KT, DT](ABC, TagModel):
    
    num: float
    folder: Path
    name: str = ""
    upload_date: str = ""
    translator: str = ""
    language: str = "en"
    

    is_read: bool = False

    _signals: AbstractChapterSignals = PrivateAttr(
        default_factory=AbstractChapterSignals
    )
    
    _repo: ChapterDataRepository[KT, DT] = PrivateAttr(None)

    def set_is_read(self, is_read: bool = True):
        self._changed = True
        self.is_read = is_read
        self._signals.is_read_changed.emit(self.is_read)

    def __str__(self) -> str:
        return f"Chapter {self.num}{f': {self.name}' if self.name else ''}"
