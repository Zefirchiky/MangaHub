from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtSvg import QSvgRenderer
from loguru import logger
from utils import MM


class SvgIcon(QIcon):
    def __init__(self, file: Path):
        if isinstance(file, Path):
            super().__init__(str(file.absolute()))
        elif isinstance(file, str):
            super().__init__(file)
            file = Path(file)
            
        try:
            with file.open("r") as f:
                self.svg_content = f.read()
        except FileNotFoundError as e:
            MM.show_message('error', str(e), 5000)
            logger.error(str(e))
            return

    def get_svg_with_color(self, color, fill = 'none'):
        return self.svg_content.replace('stroke="currentColor"', f'stroke="{color}"').replace('fill="none', f'fill="{fill}')
    
    def get_pixmap_with_color(self, color, fill = 'none'):
        size = (512, 512)
        svg_content = self.get_svg_with_color(color, fill)

        if not svg_content:
            pixmap = QPixmap(*size)
            pixmap.fill(Qt.transparent)
            return pixmap
        
        renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
        
        pixmap = QPixmap(*size)
        pixmap.fill(Qt.transparent)  # Ensure background is transparent
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap
    
    def get_icon(self, color, fill = 'none'):
        return QIcon(self.get_pixmap_with_color(color, fill))
    
    def get_pixmap(self, color, w=32, h=32, fill = 'none'):
        return self.get_icon(color, fill).pixmap(h, w)

