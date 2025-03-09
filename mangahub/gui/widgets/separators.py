from config import CM
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame


class Separator(QFrame):
    def __init__(self, orientation='h', thickness=2, padding=5, color=None, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.thickness = thickness
        self.padding = padding
        self.color = QColor(color or CM().icon)
        
        if self.orientation.lower() == 'h':
            self.setFixedHeight(self.thickness)
        else:
            self.setFixedWidth(self.thickness)
        
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        
        if self.orientation == 'h':
            painter.drawRect(self.padding, 0, self.width() - 2*self.padding, self.thickness)
        else:
            painter.drawRect(0, self.padding, self.thickness, self.height() - 2*self.padding)