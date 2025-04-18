from queue import Queue

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (QComboBox, QGraphicsPixmapItem, QGraphicsScene,
                               QGraphicsRectItem, QPushButton)

from loguru import logger

from ui.widgets.svg import SvgIcon
from directories import ICONS_DIR
from models.manga import Manga, MangaChapter, ChapterImage
from .smooth_graphics_view import SmoothGraphicsView
from config import AppConfig


class MangaViewerScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.render
        self._image_items: dict[int, QGraphicsPixmapItem] = {}
        self._pending_images: dict[int, QPixmap] = {}
        self._temp_placeholder_storage: dict[int, QPixmap] = {}
        self.cur_index = -1
        self.cur_y = 0
        
        self._width = 0
        self._height = 0
        
        self._image_queue = Queue()
        self._image_timer = QTimer(self)
        self._image_timer.timeout.connect(self._replace_placeholder)
        self._image_processing = False
        
        self._placeholder_queue = Queue()
        self._placeholder_timer = QTimer(self)
        self._placeholder_timer.timeout.connect(self._add_placeholder)
        self._placeholder_processing = False
        
    def add_placeholder(self, index: int, pixmap: QPixmap) -> bool:
        self._placeholder_queue.put((index, pixmap))
        if not self._placeholder_processing:
            self._placeholder_processing = True
            self._placeholder_timer.start(AppConfig.UI.placeholder_loading_intervals())
            
    def _add_placeholder(self) -> bool:
        if not self._placeholder_queue.empty():
            index, pixmap = self._placeholder_queue.get()
            item = QGraphicsPixmapItem(pixmap if index not in self._pending_images else self._pending_images.pop(index))
            item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            
            if index - 1 == self.cur_index: # If current index is 1 more that prev
                self.cur_index += 1
                item.setPos(-pixmap.width() // 2, self.cur_y)
                self.cur_y += item.boundingRect().height()
                self.addItem(item)
                self._image_items[index] = item
                
                if self._temp_placeholder_storage:
                    keys = sorted(list(self._temp_placeholder_storage.keys()))
                    pixmap = self._temp_placeholder_storage.pop(keys[0])
                    is_added = self.add_placeholder(keys[0], pixmap)
                    if not is_added:
                        return False
                
                return True
                
            else:
                self._temp_placeholder_storage[index] = pixmap
                return False
            
        else:
            self._placeholder_processing = False
            self._placeholder_timer.stop()
            
    def replace_placeholder(self, index: int, pixmap: QPixmap):
        self._image_queue.put((index, pixmap))
        if not self._image_processing:
            self._image_processing = True
            self._image_timer.start(AppConfig.UI.image_loading_intervals())
            
    def _replace_placeholder(self):
        if not self._image_queue.empty():
            index, pixmap = self._image_queue.get()
            if placeholder := self._image_items.get(index):
                placeholder.setPixmap(pixmap)
            else:
                self._pending_images[index] = pixmap
        
        else:
            self._image_processing = False
            self._image_timer.stop()
            
    def _placeholders_load_finished(self):
        """Returns missing placeholder numbers"""
        if self._temp_placeholder_storage:
            keys = list(self._temp_placeholder_storage.keys())
            self._temp_placeholder_storage = {}
            return [i for i in range(self.cur_index+1, keys[-1]) if i not in keys]
            
    def clear(self):
        self._image_items = {}
        self.cur_index, self.cur_y = -1, 0
        super().clear()

class MangaViewer(SmoothGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = MangaViewerScene(parent)
        self.setScene(self._scene)
        
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
        self.close_button.setIcon(SvgIcon(ICONS_DIR / "close.svg").get_icon('white'))
        self.close_button.setFixedSize(32, 32)
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.move(self.width() - self.close_button.width() - 15, 10)
        
        # chapter selection
        self.chapter_selection = QComboBox(self)
        self.chapter_selection.setFixedSize(100, 32)
        self.chapter_selection.move(self.width() - self.close_button.width() - self.chapter_selection.width() - 20, 10)
        
        # prev/next
        self.next_button = QPushButton(self)
        self.next_button.setIcon(SvgIcon(ICONS_DIR / "right.svg").get_icon('white'))
        self.next_button.setFixedSize(32, 32)
        self.next_button.setIconSize(QSize(24, 24))
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.move(self.width() - self.next_button.width() - 15, self.height() - self.next_button.height() - 15)
        
        self.prev_button = QPushButton(self)
        self.prev_button.setIcon(SvgIcon(ICONS_DIR / "left.svg").get_icon('white'))
        self.prev_button.setFixedSize(32, 32)
        self.prev_button.setIconSize(QSize(24, 24))
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.move(self.width() - self.prev_button.width() - self.next_button.width() - 15, self.height() - self.prev_button.height() - 15)
        
        self.manga = None

    def add_placeholder(self, index: int, pixmap: QPixmap):
        self._scene.add_placeholder(index, pixmap)

    def replace_placeholder(self, index: int, image_data: bytes):
        img = QPixmap()
        img.loadFromData(image_data)
        self._scene.replace_placeholder(index, img)

    def set_manga(self, manga: Manga):
        self.manga = manga
        self.chapter_selection.clear()
        self.chapter_selection.addItems([f"Chapter {i}" for i in range(1, manga.last_chapter + 1)])
        
    def set_chapter(self, chapter: MangaChapter):
        self.chapter_selection.setCurrentIndex(chapter.number - 1)

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
        self._scene.clear()

    def resizeEvent(self, event):
        self.close_button.move(self.width() - self.close_button.width() - 15, 10)
        self.chapter_selection.move(self.width() - self.close_button.width() - self.chapter_selection.width() - 20, 10)
        self.prev_button.move(self.width() - self.prev_button.width() - self.prev_button.width() - 15, self.height() - self.prev_button.height() - 15)
        self.next_button.move(self.width() - self.next_button.width() - 15, self.height() - self.next_button.height() - 15)
        super().resizeEvent(event)