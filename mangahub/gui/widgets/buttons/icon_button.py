from enum import Enum
from pathlib import Path

from config import CM
from directories import ICONS_DIR
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QPushButton
from utils import SVGManipulator

from ..svg_icon import SVGIcon


class IconTypes(Enum):
    QUESTION = 'question.svg'
    CLOSE = 'close.svg'
    EDIT = 'edit.svg'
    DELETE = 'delete.svg'
    NEXT = 'left.svg'
    PREV = 'right.svg'
    EYE = 'eye.svg'
    

class IconButton(QPushButton):
    Types = IconTypes
    
    def __init__(self, icon: str | Path | IconTypes, color='white', size: int=32, fn=None, parent=None):
        super().__init__(parent=parent)
        self.set_icon(icon, color)
        self.setFixedSize(size, size)
        self.setIconSize(QSize(size - 8, size - 8))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if fn:
            self.clicked.connect(fn)
            
        self.raise_()
        
    def set_icon(self, icon: str | Path | IconTypes, color='white') -> 'IconButton':
        if isinstance(icon, Path):
            icon = str(icon)
        if isinstance(icon, IconTypes):
            icon = f'{ICONS_DIR}/{icon.value}'
        self.setIcon(SVGIcon(icon).set_hover_size_factor(1.2).set_color(color).get_pixmap())
        return self
        
    def set_size(self, size: int) -> 'IconButton':
        self.setFixedSize(size, size)
        self.setIconSize(QSize(size, size))
        return self
    
    def set_transparent(self) -> 'IconButton':
        self.setStyleSheet('''
            background-color: transparent;
            border: none;
        ''')
        return self
        