from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel

from .smooth_scroll_area import SmoothScrollArea


class LineLabel(SmoothScrollArea):
    def __init__(self, text="", parent=None, vertical=False, bar=False):
        super().__init__(parent, vertical=vertical, bar=bar)

        self.scroll_duration = 80
        self.step_size = 20

        self.label = QLabel(text, parent=self)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setCursor(Qt.CursorShape.IBeamCursor)
        self.font_ = QFont("Times", 12, 5)
        self.label.setFont(self.font_)
        self.setFixedHeight(24)

        self.setWidget(self.label)

        self.bg_color = "transparent"
        self.border_px = 0
        self.border_color = "none"

        self.set_text_color()
        self.update_style()

    def set_font(
        self,
        font: QFont | None = None,
        font_name: str = "Times",
        font_size: int = 12,
        font_weight: int = 5,
    ):
        if font:
            self.font_ = font
        else:
            self.font_ = QFont(font_name, font_size, font_weight)

        self.label.setFont(self.font_)
        self.setFixedHeight(self.font_.pointSize() * 2)
        return self

    def set_text(self, text: str):
        self.label.setText(text)
        return self

    def set_selectable(self, is_selectable: bool = False):
        self.label.setDisabled(not is_selectable)
        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            if is_selectable
            else Qt.TextInteractionFlag.NoTextInteraction
        )
        return self

    def set_text_color(self, color: str = "white"):
        self.label.setStyleSheet(f"color: {color};")
        return self

    def set_bg_color(self, color: str = "#1e1e1e"):
        self.bg_color = color
        self.update_style()
        return self

    def set_border(self, thickness: int = 0, color: str = "white"):
        self.border_px = thickness
        self.border_color = color
        self.update_style()
        return self

    def update_style(self):
        self.setStyleSheet(f"""
            background-color: {self.bg_color};
            border: {self.border_px}px solid {self.border_color};
        """)
