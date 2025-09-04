from __future__ import annotations
from enum import Enum
from pathlib import Path

from config import CM
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QPushButton

from ..svg_icon import SVGIcon
from config import Config


class IconTypes(Enum):
    QUESTION = "question.svg"
    CLOSE = "close.svg"
    EDIT = "edit.svg"
    DELETE = "delete.svg"

    NEXT = "right.svg"
    PREV = "left.svg"
    RIGHT_ARROW = "right.svg"
    LEFT_ARROW = "left.svg"

    EYE = "eye.svg"
    SEARCH = "search.svg"


class IconButton(QPushButton):
    IconTypes = IconTypes

    def __init__(
        self,
        icon: str | Path | IconTypes,
        color="white",
        size: int = 32,
        icon_size: int = -1,
        fn=None,
        parent=None,
    ):
        """
        Constructs an IconButton with the given parameters.

        :param icon: str | Path | IconTypes
            The path to the icon or the icon type from IconButton.IconTypes
        :param color: str
            The color of the icon
        :param size: int
            The size of the button
        :param icon_size: int
            The size of the icon
        :param fn: callable
            The function to call when the button is clicked
        :param parent: QWidget
            The parent of the button
        """
        super().__init__(parent=parent)
        self.set_icon(icon, color)
        self.setFixedSize(size, size)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if icon_size == -1:
            icon_size = size - 8

        if fn:
            self.clicked.connect(fn)

        self.raise_()

    def set_icon(self, icon: str | Path | IconTypes, color="white") -> IconButton:
        if isinstance(icon, IconTypes):
            icon = Config.Dirs.RESOURCES.ICONS / icon.value  # TODO(?): Use IconRepo
        self.setIcon(
            SVGIcon(Path(icon)).set_hover_size_factor(1.2).set_color(color).get_qicon()
        )
        return self

    def set_size(self, size: int) -> IconButton:
        self.setFixedSize(size, size)
        return self

    def set_icon_size(self, size: int) -> IconButton:
        self.setIconSize(QSize(size, size))
        return self

    def set_transparent(self) -> IconButton:
        self.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        return self
