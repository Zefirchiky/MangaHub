from pathlib import Path
from enum import Enum

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt, QSize

from ..svg import SvgIcon
from directories import ICONS_DIR


class IconTypes(Enum):
    CLOSE = 'close.svg'
    EDIT = 'edit.svg'
    DELETE = 'delete.svg'
    NEXT = 'left.svg'
    PREV = 'right.svg'
    

class ActionButton(QPushButton):
    Types = IconTypes
    
    def __init__(self, icon: str | Path | IconTypes, fn=None, size: int=32, parent=None):
        super().__init__(parent=parent)
        if isinstance(icon, Path):
            icon = str(icon)
        if isinstance(icon, IconTypes):
            icon = f'{ICONS_DIR}/{icon.value}'
        self.setIcon(SvgIcon(icon).get_icon('white'))
        self.setFixedSize(size, size)
        self.setIconSize(QSize(size - 8, size - 8))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if fn:
            self.clicked.connect(fn)
            
        self.raise_()
        
    def set_size(self, size: int):
        self.setFixedSize(size, size)
        self.setIconSize(QSize(size, size))
        