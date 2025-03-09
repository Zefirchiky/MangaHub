from pathlib import Path

from directories import ICONS_DIR
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy

from ..scroll_areas import LineLabel
from ..separators import Separator
from ..svg_icon import IconRepo, SVGIcon


class ChapterButton(QPushButton):
    def __init__(self, text: str='button', parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setContentsMargins(5, 0, 5, 0)
        self.setFixedHeight(24)
        
        self._text = LineLabel(text).set_selectable(False)
        
        self.root = QHBoxLayout()
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.addWidget(self._text)
        self.root.addStretch()
        self.setLayout(self.root)
        
        self.is_eye = False
        
    def add_eye(self, is_on=True):
        if not self.is_eye:
            self.root.insertWidget(0, IconRepo.get_icon('eye'))
            self.root.insertWidget(1, Separator('v', thickness=1))
        self.is_eye = True
        return self