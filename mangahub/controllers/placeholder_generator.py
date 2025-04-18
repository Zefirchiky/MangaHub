from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QFont
from config import CM


class PlaceholderGenerator:
    @staticmethod
    def static(width: int, height: int, text: str='', color: QColor=QColor('#202020')):  # Use ColorManager
        pixmap = QPixmap(width, height)
        pixmap.fill(CM.transparent)
        
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(120))
        painter.fillRect(0, 0, width, height, gradient)
        
        if text:
            font = QFont("Arial", 12)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            painter.setFont(font)
            painter.setPen(QColor(220, 220, 220, 180))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
                    
        painter.end()
        return pixmap