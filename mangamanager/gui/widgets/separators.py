from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class Separator(QFrame):
    def __init__(self, orientation=Qt.Horizontal, color="gray", thickness=1, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.color = QColor(color)
        self.thickness = thickness
        
        if self.orientation == Qt.Horizontal:
            self.setFixedHeight(self.thickness)
        else:
            self.setFixedWidth(self.thickness)
        
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        
        if self.orientation == Qt.Horizontal:
            painter.drawRect(0, 0, self.width(), self.thickness)
        else:
            painter.drawRect(0, 0, self.thickness, self.height())