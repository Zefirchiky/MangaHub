from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage, QColor
from .smooth_graphics_view import SmoothGraphicsView
from gui.gui_utils import MM
from gui.widgets import SvgIcon
from utils import BatchWorker, convert_to_format
from directories import *
import io


class MangaViewer(SmoothGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._vertical_spacing = 0
        self._base_width = 480
        self._current_scale = 0.7
        self._zoom_factor = 1.1
        
        self._image_items = []
        self._placeholders = []
        
        self.scale_multiplier = self._current_scale
        self.scale(self._current_scale, self._current_scale)
        
        # close
        self.close_button = QPushButton(self)
        self.close_button.setIcon(SvgIcon(f"{ICONS_DIR}/close-outline.svg").get_icon('white'))
        self.close_button.setFixedSize(32, 32)
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.move(self.width() - self.close_button.width() - 15, 10)
        
        # prev/next
        self.next_button = QPushButton(self)
        self.next_button.setIcon(SvgIcon(f"{ICONS_DIR}/chevron-forward-outline.svg").get_icon('white'))
        self.next_button.setFixedSize(32, 32)
        self.next_button.setIconSize(QSize(24, 24))
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.move(self.width() - self.next_button.width() - 15, self.height() - self.next_button.height() - 15)
        
        self.prev_button = QPushButton(self)
        self.prev_button.setIcon(SvgIcon(f"{ICONS_DIR}/chevron-back-outline.svg").get_icon('white'))
        self.prev_button.setFixedSize(32, 32)
        self.prev_button.setIconSize(QSize(24, 24))
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.move(self.width() - self.prev_button.width() - self.next_button.width() - 15, self.height() - self.prev_button.height() - 15)

    def add_placeholder(self, width, height, y_pos):
        placeholder = QGraphicsRectItem((0 - width) // 2, y_pos, width, height)
        placeholder.setBrush(QColor(200, 200, 200, 50))  # Light grey placeholder
        self.scene.addItem(placeholder)
        self._placeholders.append(placeholder)

    def replace_placeholder(self, index, image_data):
        if index >= len(self._placeholders):
            return

        placeholder = self._placeholders[index]
        self.scene.removeItem(placeholder)
        self._placeholders[index] = None 

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
        
    def clear(self):
        self.verticalScrollBar().setValue(0)
        self._image_items = []
        self._placeholders = []
        self.scene.clear()

    def resizeEvent(self, event):
        self.close_button.move(self.width() - self.close_button.width() - 15, 10)
        self.prev_button.move(self.width() - self.prev_button.width() - self.prev_button.width() - 15, self.height() - self.prev_button.height() - 15)
        self.next_button.move(self.width() - self.next_button.width() - 15, self.height() - self.next_button.height() - 15)
        super().resizeEvent(event)