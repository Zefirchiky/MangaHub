from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class Separator(QFrame):
    def __init__(self, orientation=Qt.Orientation.Horizontal, color="gray", thickness=1, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.color = QColor(color)
        self.thickness = thickness
        
        if self.orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(self.thickness)
        else:
            self.setFixedWidth(self.thickness)
        
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        
        if self.orientation == Qt.Orientation.Horizontal:
            painter.drawRect(0, 0, self.width(), self.thickness)
        else:
            painter.drawRect(0, 0, self.thickness, self.height())