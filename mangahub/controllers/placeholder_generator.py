from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QFont
from config import CM


# TODO: Wrong file place
class PlaceholderGenerator:
    _cached_pixmaps: dict[str, QPixmap] = {}
    
    @classmethod
    def static(cls, width: int, height: int, text: str='', color: QColor=QColor('#202020')):  # Use ColorManager
        name = f'{width}_{height}_{color.name()}'
        if pixmap := cls._cached_pixmaps.get(name):
            return pixmap
        
        pixmap = QPixmap(width, height)
        pixmap.fill(CM.transparent)
        
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(120))
        painter.fillRect(0, 0, width, height, gradient)
        
        cls._cached_pixmaps[name] = pixmap
        
        if text:
            font = QFont("Arial", 12)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            painter.setFont(font)
            painter.setPen(QColor(220, 220, 220, 180))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
                    
        painter.end()
        return pixmap