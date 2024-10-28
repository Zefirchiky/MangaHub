from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QColor
from .smooth_graphics_view import SmoothGraphicsView
from gui.gui_utils import MM
from utils import BatchWorker, convert_to_format
import io


class MangaViewer(SmoothGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_items = []
        self._vertical_spacing = 0
        self._base_width = 480
        self._current_scale = 0.7
        self._zoom_factor = 1.1
        
        self._placeholders = []
        
        self.scale_multiplier = self._current_scale
        self.scale(self._current_scale, self._current_scale)

    def add_placeholder(self, width, height, y_pos):
        placeholder = QGraphicsRectItem((0 - width) // 2, y_pos, width, height)
        placeholder.setBrush(QColor(200, 200, 200, 50))  # Light grey placeholder
        self.scene.addItem(placeholder)
        self._placeholders.append(placeholder)

    def replace_placeholder(self, index, image_data):
        if index >= len(self._placeholders):
            return

        # Remove the placeholder
        placeholder = self._placeholders[index]
        self.scene.removeItem(placeholder)
        self._placeholders[index] = None  # Optional: mark as replaced

        # Add the actual image in its place
        pixmap = QPixmap()
        if pixmap.loadFromData(image_data):
            item = QGraphicsPixmapItem(pixmap)
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            item.setPos(placeholder.rect().x(), placeholder.rect().y())
            self.scene.addItem(item)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            
            factor = self._zoom_factor if zoom_in else 1 / self._zoom_factor
            new_scale = self._current_scale * factor
            
            if 0.2 <= new_scale <= 5.0:
                self.scale_multiplier = new_scale
                old_pos = self.mapToScene(event.position().toPoint())
                
                self.resetTransform()
                self._current_scale = new_scale
                self.scale(new_scale, new_scale)
                
                # Get new scene position and adjust view to keep point under mouse
                new_pos = self.mapToScene(event.position().toPoint())
                delta = new_pos - old_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + int(delta.x()))
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + int(delta.y()))
                
                event.accept()
                
            return
                
        super().wheelEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)