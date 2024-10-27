from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
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
        
        self.scale(self._current_scale, self._current_scale)

    def add_images(self, image_bytes_list):
        worker = BatchWorker()
        pixmap_list = worker.process_batch(self.get_pixmap, image_bytes_list)
        
        current_y = 0
        for pixmap in pixmap_list:
            viewport_width = self.viewport().width()
            image_x = (viewport_width - pixmap.width()) / 2

            item = QGraphicsPixmapItem(pixmap)
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            item.setPos(image_x, current_y)
            self.scene.addItem(item)
            self._image_items.append(item)
            current_y += pixmap.height() + self._vertical_spacing

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        
    def get_pixmap(self, image_bytes):
        image_bytes = convert_to_format(image_bytes)
        image = QImage()
        if not image.loadFromData(image_bytes):
            MM.show_message('error', 'Failed to load image')
            return 
        return QPixmap.fromImage(image)

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