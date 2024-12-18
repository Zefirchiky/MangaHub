from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from .smooth_scroll_area import SmoothScrollArea


class LineLabel(SmoothScrollArea):
    def __init__(self, text="", parent=None, vertical=False, bar=False):
        super().__init__(parent, vertical=vertical, bar=bar)
        self.scroll_duration = 80
        self.step_size = 20

        self.label = QLabel(text, parent=self)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setCursor(Qt.CursorShape.IBeamCursor)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.font_ = QFont("Times", 12, 5)
        self.label.setFont(self.font_)
        self.setFixedHeight(24)
        
        self.setWidget(self.label)
        
    def set_font(self, font: QFont=None, font_name: str="Times", font_size: int=12, font_weight: int=5):
        if font:
            self.font_ = font
        else:
            self.font_ = QFont(font_name, font_size, font_weight)
        
        self.label.setFont(self.font_)
        self.setFixedHeight(self.font_.pointSize() * 2)
        
    def setText(self, text: str):
        self.label.setText(text)