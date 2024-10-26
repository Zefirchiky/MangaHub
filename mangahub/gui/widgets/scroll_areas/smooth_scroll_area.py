from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt
from .smooth_scroll_mixin import SmoothScrollMixin


class SmoothScrollArea(QScrollArea, SmoothScrollMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_smooth_scroll()
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)