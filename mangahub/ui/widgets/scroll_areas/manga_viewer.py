from queue import Queue
import heapq

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QPushButton,
    QSizePolicy
)

from loguru import logger

from ui.widgets.svg_icon import IconRepo
from models.manga import Manga, MangaChapter
from .smooth_graphics_view import SmoothGraphicsView
from utils import MM
from config import AppConfig
from icecream import ic


class MangaViewerScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_items: dict[int, QGraphicsPixmapItem] = {}
        self._pending_images: dict[int, QPixmap] = {}
        self._temp_placeholder_storage: dict[int, QPixmap] = {}
        self._cur_index = -1
        self._cur_y = 0

        self._image_queue = Queue()
        self._image_timer = QTimer(self)
        self._image_timer.timeout.connect(self._replace_placeholder)
        self._image_processing = False

        self._placeholder_queue = []    # ! heapq is used for fast smallest element
        self._placeholder_timer = QTimer(self)
        self._placeholder_timer.timeout.connect(self._add_placeholder)
        self._placeholder_processing = False

    def add_placeholder(self, index: int, pixmap: QPixmap) -> bool:
        heapq.heappush(self._placeholder_queue, (index, pixmap))
            
        if not self._placeholder_processing:
            self._placeholder_processing = True
            self._placeholder_timer.start(AppConfig.UI.placeholder_loading_intervals())

    def _add_placeholder(self) -> bool:
        if not self._placeholder_queue:
            self._placeholder_processing = False
            self._placeholder_timer.stop()
            return False
        
        index, pixmap = heapq.heappop(self._placeholder_queue)
        pending_pixmap = self._pending_images.pop(index, pixmap)
        item = QGraphicsPixmapItem(pending_pixmap)
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

        if index - 1 == self._cur_index:
            self._cur_index += 1
            item.setPos(-pending_pixmap.width() // 2, self._cur_y)
            self._cur_y += item.boundingRect().height()
            self.addItem(item)
            self._image_items[index] = item

            if self._temp_placeholder_storage:
                next_index = min(self._temp_placeholder_storage)
                next_pixmap = self._temp_placeholder_storage.pop(next_index)
                if not self.add_placeholder(next_index, next_pixmap):
                    return False

            return True

        self._temp_placeholder_storage[index] = pending_pixmap
        return False

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
            return [i for i in range(self._cur_index + 1, keys[-1]) if i not in keys]


class MangaViewer(SmoothGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._scene = MangaViewerScene(self)
        self.setScene(self._scene)

        self._vertical_spacing = 0
        self._base_width = 480
        self._current_scale = 0.7
        self._zoom_factor = 1.1

        self.scale_multiplier = self._current_scale
        self.scale(self._current_scale, self._current_scale)

        self._setup_ui()
        self.manga = None
        self.chapter = None

    def _setup_ui(self):
        self.close_button = self._create_button(
            IconRepo.Icons.CLOSE, (32, 32), (self.width() - 47, 10)
        )

        self.chapter_selection = QComboBox(self)
        self.chapter_selection.setFixedSize(100, 32)
        self.chapter_selection.move(self.width() - 167, 10)

        self.next_button = self._create_button(
            IconRepo.Icons.R_ARROW,
            (32, 32),
            (self.width() - 47, self.height() - 47),
        )

        self.prev_button = self._create_button(
            IconRepo.Icons.L_ARROW,
            (32, 32),
            (self.width() - 79, self.height() - 47),
        )

    def _create_button(self, icon, size, position):
        button = QPushButton(self)
        button.setIcon(IconRepo.get(icon).get_qicon())
        button.setFixedSize(*size)
        button.setIconSize(QSize(24, 24))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.move(*position)
        return button

    def add_placeholder(self, index: int, pixmap: QPixmap):
        self._scene.add_placeholder(index, pixmap)

    def replace_placeholder(self, index: int, image_data: bytes):
        img = QPixmap()
        img.loadFromData(image_data)
        self._scene.replace_placeholder(index, img)

    def _on_chapter_loaded(self):
        if missing := self._scene._placeholders_load_finished():
            MM.show_warning(
                f"Some images are missing while loading {self.manga} - {self.chapter}: {missing}"
            )

    def set_manga(self, manga: Manga):
        self.manga = manga
        self.chapter_selection.clear()
        self.chapter_selection.addItems(
            [f"Chapter {i}" for i in range(1, manga.last_chapter + 1)]
        )

    def set_chapter(self, chapter: MangaChapter):
        self.chapter = chapter
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

                new_pos = self.mapToScene(event.position().toPoint())
                delta = new_pos - old_pos
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() + int(delta.x())
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() + int(delta.y())
                )

                event.accept()
            return

        super().wheelEvent(event)

    def clear(self):
        self.verticalScrollBar().setValue(0)
        self._scene = MangaViewerScene(self)
        self.setScene(self._scene)

    def resizeEvent(self, event):
        self.close_button.move(self.width() - self.close_button.width() - 15, 10)
        self.chapter_selection.move(
            self.width()
            - self.close_button.width()
            - self.chapter_selection.width()
            - 20,
            10,
        )
        self.prev_button.move(
            self.width() - self.prev_button.width() - self.next_button.width() - 15,
            self.height() - self.prev_button.height() - 15,
        )
        self.next_button.move(
            self.width() - self.next_button.width() - 15,
            self.height() - self.next_button.height() - 15,
        )
        super().resizeEvent(event)
