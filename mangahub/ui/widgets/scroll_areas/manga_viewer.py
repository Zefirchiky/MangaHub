from __future__ import annotations
from queue import Queue
import heapq

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsPixmapItem,
    QGraphicsTextItem,
    QGraphicsScene,
    QPushButton,
    QSizePolicy,
)

from loguru import logger

from ui.widgets.svg_icon import IconRepo
from ui.widgets.buttons import IconButton
from models.images import ImageMetadata
from models.manga import Manga, MangaChapter
from .smooth_graphics_view import SmoothGraphicsView
from resources.enums import StorageSize
from utils import MM, PlaceholderGenerator
from config import Config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui import MainWindow


class MangaViewerScene(QGraphicsScene):
    images_request = Signal(set)

    def __init__(self, parent: MangaViewer):
        super().__init__(parent)

        self._image_items: dict[int, tuple[QGraphicsPixmapItem, int, int]] = {}
        self._visible_image_indexes: set[int] = set()
        self._cur_index = -1
        self._cur_y = 0

        self._placeholder_queue: list[
            tuple[int, int, int]
        ] = []  # ! heapq is used for fast smallest element
        self._placeholder_timer = QTimer(self)
        self._placeholder_timer.timeout.connect(self._add_placeholder)

        self.width_ = 0
        self._scale = 1.0

        if Config.debug_mode():
            self._images_debug_text = {}

    def add_placeholder(self, index: int, width: int, height: int) -> None:
        heapq.heappush(self._placeholder_queue, (index, width, height))

        if not self._placeholder_timer.isActive():
            self._placeholder_timer.start(
                Config.Performance.MangaViewer.placeholder_loading_intervals()
            )

    def _add_placeholder(self) -> bool:
        if not self._placeholder_queue:
            if not Config.Performance.MangaViewer.set_size_with_every_placeholder():
                self.setSceneRect(-self.width_ // 2, 0, self.width_, self._cur_y)
            self._placeholder_timer.stop()
            return False

        i = self._placeholder_queue[0][0]
        if not self._cur_index == i - 1:  # If lowest index is not next
            return False

        i, width, height = heapq.heappop(self._placeholder_queue)
        if width > self.width_:
            self.width_ = width

        pm = QPixmap(width, height)
        item = QGraphicsPixmapItem(pm)
        item.setCacheMode(QGraphicsPixmapItem.CacheMode.DeviceCoordinateCache)
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        item.setPos(-width // 2, self._cur_y)
        item.setVisible(False)

        if Config.debug_mode():
            self._add_images_debug_info(i, self._cur_y + 10, width // 2 + 6, pm)

        self._image_items[i] = (item, height, width)
        self.addItem(item)
        self._cur_y += height
        self._cur_index += 1
        if Config.Performance.MangaViewer.set_size_with_every_placeholder():
            self.setSceneRect(-self.width_ // 2, 0, self.width_, self._cur_y)
        return True

    def _add_images_debug_info(self, i, y, x, pm: QPixmap):
        text = (
            f"#{i}: {pm.width()}x{pm.height()}\n"
            f"{StorageSize((pm.width() * pm.height() * pm.depth()) // 8)} ({pm.width() * pm.height() * pm.depth()} Bits)"
        )
        item = QGraphicsTextItem(text)
        item.setPos(x, y)
        font = QFont("Roboto", 12)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        item.setFont(font)
        self.addItem(item)
        self._images_debug_text[i] = item

    def replace_placeholder(self, i: int, image: QPixmap):
        if i in self._visible_image_indexes:
            self.set_image(i, image)

    def set_image(self, i: int, image: QPixmap):
        self._image_items[i][0].setPixmap(image)

    def _placeholders_load_finished(self):
        """Returns missing placeholder numbers"""
        if self._placeholder_queue:
            indexes = [i[0] for i in self._placeholder_queue]
            return [
                i for i in range(self._cur_index + 1, indexes[-1]) if i not in indexes
            ]

    def _cull_images(self, y: int | float, height: int | float, multiplier: float):
        y //= self._scale
        height //= self._scale
        offscreen_height = height * (multiplier - 1)
        y1, y2 = y - offscreen_height, y + height + offscreen_height

        indexes = self._get_image_items_in_range(y1, y2)
        for i in indexes:
            if i in self._visible_image_indexes:
                continue

            self._image_items[i][0].setVisible(True)

        for i in (
            self._visible_image_indexes - indexes
        ):  # {1, 2, 3, 4} - {3, 4, 5, 6} = {1, 2}  Indexes that were visible, but not anymore
            item, width, height = self._image_items[i]
            item.setPixmap(QPixmap(width, height))
            item.setVisible(False)

        self.images_request.emit(
            indexes - self._visible_image_indexes
        )  # {3, 4, 5, 6} - {1, 2, 3, 4} = {5, 6}  Indexes that are visible, but lack images
        self._visible_image_indexes = indexes

    def _get_image_items_in_range(self, y1, y2) -> set[int]:
        indexes = set()
        cur_y = -1
        for i, (
            image,
            height,
            _,
        ) in self._image_items.items():  # TODO: Binary tree
            if cur_y != -1:
                if cur_y > y2:  # If current image is out of bounds
                    return indexes

                cur_y += height
                indexes.add(i)

            elif self._is_image_in_range(i, y1, y2):
                cur_y = image.y()
                indexes.add(i)
                continue

        return indexes

    def _is_image_in_range(self, i, y1, y2):  # y1 - upper bound, y2 - lower
        item, height, _ = self._image_items[i]
        if item.y() + height > y1 and item.y() < y2:
            return True
        return False


class MangaViewer(SmoothGraphicsView):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.parent_ = parent
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
        self._image_cache = self.parent_.app_controller.manga_manager.images_cache
        self._image_indexes_names = {}
        self._indexes_cull = set()

        self._cull_queued = False
        self._cull_allowed = True
        self.verticalScrollBar().valueChanged.connect(self._cull_scene)

    def _setup_ui(self):
        self.close_button = IconButton(IconButton.IconTypes.CLOSE, parent=self)
        self.close_button.move(self.width() - 47, 10)

        self.chapter_selection = QComboBox(self)
        self.chapter_selection.setFixedSize(100, 32)
        self.chapter_selection.move(self.width() - 167, 10)

        self.next_button = IconButton(IconButton.IconTypes.NEXT, parent=self)
        self.next_button.move(self.width() - 47, self.height() - 47)

        self.prev_button = IconButton(IconButton.IconTypes.PREV, parent=self)
        self.prev_button.move(self.width() - 79, self.height() - 47)

    def set_manga(self, manga: Manga):
        self.manga = manga
        self.chapter_selection.clear()
        self.chapter_selection.addItems(
            [f"Chapter {i}" for i in manga._chapters_repo.get_all()]
        )

    def set_chapter(self, chapter: MangaChapter):
        self.chapter = chapter
        self.chapter_selection.setCurrentIndex(int(chapter.num - 1))

    def add_placeholder(self, index: int, width: int, height: int):
        self._scene.add_placeholder(index, width, height)
        if index < 5:
            self._indexes_cull.add(index)
        if len(self._indexes_cull) == 5 and not index > 5:
            self._cull_scene()

    def replace_placeholder(self, index: int, name: str):
        self._image_indexes_names[index] = name
        img = QPixmap()
        img.loadFromData(self._image_cache.get(name))
        self._scene.replace_placeholder(index, img)

    def _on_images_request(self, indexes: set[int]):
        for i in indexes:
            try:
                image_bytes = self._image_cache.get(
                    self._image_indexes_names.get(i, "")
                )
                image = QPixmap()
                image.loadFromData(image_bytes)
            except Exception:
                meta = self.chapter.get_data_repo().get(i).metadata
                image = PlaceholderGenerator.static(
                    meta.width, meta.height, f"Num {i}\n{meta.width}x{meta.height}"
                )  # type: ignore

            self._scene.set_image(i, image)

    def _on_chapter_loaded(self):
        self._cull_scene()
        if missing := self._scene._placeholders_load_finished():
            MM.show_warning(
                f"Some images are missing while loading {self.manga} - {self.chapter}: {missing}"
            )

    def _cull_cooldown_timer_out(self):
        self._cull_allowed = True
        if self._cull_queued:
            self._cull_scene()
            self._cull_queued = False

    def _cull_scene(self):  # TODO: Doesn't work properly on large images
        if not self.chapter:
            return

        if not self._cull_allowed:
            self._cull_queued = True
            return

        # Get current scroll position and viewport size
        scrollbar = self.verticalScrollBar()
        current = scrollbar.value()
        viewport_height = self.viewport().height()

        self._scene._cull_images(
            current,
            viewport_height,
            Config.Performance.MangaViewer.cull_height_multiplier(),
        )
        QTimer.singleShot(
            Config.Performance.MangaViewer.cull_scene_cooldown(),
            self._cull_cooldown_timer_out,
        )
        self._cull_allowed = False

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            factor = self._zoom_factor if zoom_in else 1 / self._zoom_factor
            new_scale = self._current_scale * factor

            if 0.2 <= new_scale <= 5.0:
                self.scale_multiplier = new_scale
                self._scene._scale = new_scale
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

                self._cull_scene()
                event.accept()
            return

        super().wheelEvent(event)

    def clear(self):
        self.verticalScrollBar().setValue(0)
        self._scene = MangaViewerScene(self)
        self._scene._scale = self.scale_multiplier
        self._scene.images_request.connect(self._on_images_request)
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
