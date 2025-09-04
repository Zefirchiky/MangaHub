from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy

from ..scroll_areas import LineLabel
from ..separators import Separator
from ..svg_icon import IconRepo, SVGIcon

from core.models.abstract import AbstractChapter


class ChapterButton(QPushButton):
    def __init__(self, text: str = "button", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setContentsMargins(5, 0, 5, 0)
        self.setFixedHeight(24)

        self._text = LineLabel(text).set_selectable(False).set_font(font_size=10)

        self.root = QHBoxLayout()
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.addWidget(self._text)
        self.root.addStretch()
        self.setLayout(self.root)

        self.eye_icon: SVGIcon | None = None

        self.chapter: AbstractChapter | None = None

    def add_eye(self, is_on=True) -> ChapterButton:
        if not self.eye_icon:
            self.eye_icon = IconRepo.get("eye").change_icon(int(is_on))
            self.root.insertWidget(0, self.eye_icon)
            self.root.insertWidget(1, Separator("v", thickness=1))
        return self

    def set_text(self, text: str) -> ChapterButton:
        self._text.set_text(text)
        return self

    def set_chapter(self, chapter: AbstractChapter) -> ChapterButton:
        self.chapter = chapter
        self.set_text(str(chapter))
        if self.eye_icon:
            self.eye_icon.change_icon(chapter.is_read)
            self.chapter._signals.is_read_changed.connect(
                lambda is_read: self.eye_icon.change_icon(is_read)
            )
            self.eye_icon.pressed.connect(
                lambda: chapter.set_is_read(self.eye_icon._is_second_icon)
            )
        return self
