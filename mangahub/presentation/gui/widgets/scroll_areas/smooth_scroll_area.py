from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea

from .smooth_scroll_mixin import SmoothScrollMixin


class SmoothScrollArea(QScrollArea, SmoothScrollMixin):
    def __init__(self, parent=None, vertical=True, bar=True):
        super().__init__(parent)
        self.init_smooth_scroll(vertical=vertical)

        self.setWidgetResizable(True)
        horizontal_policy, vertical_policy = (
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        if bar:
            horizontal_policy = (
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                if vertical
                else Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            vertical_policy = (
                Qt.ScrollBarPolicy.ScrollBarAlwaysOn
                if vertical
                else Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
        self.setHorizontalScrollBarPolicy(horizontal_policy)
        self.setVerticalScrollBarPolicy(vertical_policy)
        self.update()

    def wheelEvent(self, event):
        SmoothScrollMixin.wheelEvent(self, event)
