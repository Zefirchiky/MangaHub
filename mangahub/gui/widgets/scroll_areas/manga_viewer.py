from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget, QLabel
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from .animated_scroll_area import AnimatedScrollArea


class MangaViewer(AnimatedScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.img_width = 480

        self.root_layout = QHBoxLayout()
        self.root_layout.setSpacing(0)
        
        root_widget = QWidget()
        root_widget.setLayout(self.root_layout)
        self.setWidget(root_widget)
        
    def add_image(self, image: bytes, size_multiplier: float = 1.0):
        image_pmap = QPixmap(image)
        image_pmap = image_pmap.scaledToWidth(self.img_width * size_multiplier, Qt.TransformationMode.SmoothTransformation)
        
        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setPixmap(image_pmap)
        
        self.root_layout.addWidget(img)
        