from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtSvg import QSvgRenderer
from bs4 import BeautifulSoup


class SvgIcon(QIcon):
    def __init__(self, file):
        super().__init__(file)
        try:
            with open(file, "r") as f:
                self.svg_content = f.read()
        except FileNotFoundError:
            print("Error: 'icon.svg' file not found.")
            return ""

    def get_svg_with_color(self, color, fill = 'none'):
        return self.svg_content.replace('stroke="currentColor"', f'stroke="{color}"').replace('fill="none', f'fill="{fill}')
    
    def get_pixmap(self, color, fill = 'none'):
        size = (512, 512)
        svg_content = self.get_svg_with_color(color, fill)

        if not svg_content:
            # Return a transparent pixmap if SVG content is empty
            pixmap = QPixmap(*size)
            pixmap.fill(Qt.transparent)
            return pixmap
        
        # Create a QSvgRenderer from the modified SVG content
        renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
        
        # Create a QPixmap to render the SVG
        pixmap = QPixmap(*size)
        pixmap.fill(Qt.transparent)  # Ensure background is transparent
        
        # Render the SVG onto the pixmap using QPainter
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap
    
    def get_icon(self, color, fill = 'none'):
        return QIcon(self.get_pixmap(color, fill))

