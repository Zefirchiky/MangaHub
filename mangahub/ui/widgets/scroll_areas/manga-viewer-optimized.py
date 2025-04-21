from queue import Queue
import heapq
import sys
from functools import lru_cache
import gc

from PySide6.QtCore import QSize, Qt, QTimer, QRect
from PySide6.QtGui import QColor, QPixmap, QImage
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
from resources.enums import StorageSize
from utils import MM
from config import AppConfig


class ImageCache:
    """LRU cache for images with size-based eviction"""
    
    def __init__(self, max_memory_mb=200):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.current_memory = 0
        self.cache = {}
        self.access_order = []  # LRU tracking
    
    def get(self, key):
        """Get image from cache if available"""
        if key in self.cache:
            # Update access order (move to end of list)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, pixmap):
        """Add image to cache with memory tracking and eviction"""
        # Calculate image memory size (approximation)
        img_memory = pixmap.width() * pixmap.height() * 4  # 4 bytes per pixel (32-bit)
        
        # If this single image is too large, don't cache it
        if img_memory > self.max_memory * 0.5:
            logger.warning(f"Image {key} is too large to cache ({img_memory/(1024*1024):.2f}MB)")
            return
            
        # Evict images until we have space
        while self.current_memory + img_memory > self.max_memory and self.access_order:
            oldest_key = self.access_order.pop(0)
            evicted_pixmap = self.cache.pop(oldest_key)
            # Calculate size of evicted image
            evicted_memory = evicted_pixmap.width() * evicted_pixmap.height() * 4
            self.current_memory -= evicted_memory
            logger.debug(f"Evicted image {oldest_key}, freed {evicted_memory/(1024*1024):.2f}MB")
            
        # Add new image to cache
        self.cache[key] = pixmap
        self.access_order.append(key)
        self.current_memory += img_memory
        logger.debug(f"Cached image {key}, size: {img_memory/(1024*1024):.2f}MB, total: {self.current_memory/(1024*1024):.2f}MB")
    
    def clear(self):
        """Clear all cached images"""
        self.cache.clear()
        self.access_order.clear()
        self.current_memory = 0
        gc.collect()  # Force garbage collection


class MangaViewerScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Single storage for visible images
        self._image_items = {}
        
        # Use a small queue for pending operations
        self._image_queue = Queue(maxsize=10)
        self._image_timer = QTimer(self)
        self._image_timer.timeout.connect(self._process_image_queue)
        self._image_processing = False
        
        # Track layout information
        self._cur_index = -1
        self._cur_y = 0
        
        # Create image cache with configurable size limit
        self._image_cache = ImageCache(max_memory_mb=AppConfig.UI.get("cache_size_mb", 200))
        
        # Viewport tracking for culling
        self._visible_rect = QRect()
        
    def set_visible_rect(self, rect):
        """Update the current visible viewport rectangle for culling"""
        self._visible_rect = rect
        self._cull_invisible_items()
        
    def _cull_invisible_items(self):
        """Remove items that are far outside the viewport"""
        if not self._visible_rect.isValid():
            return
            
        # Define culling boundaries with buffer
        buffer = self._visible_rect.height() * 2  # 2x viewport height buffer
        visible_top = self._visible_rect.top() - buffer
        visible_bottom = self._visible_rect.bottom() + buffer
        
        # Create a list of items to remove (can't modify dict during iteration)
        to_remove = []
        for idx, item in self._image_items.items():
            item_rect = item.sceneBoundingRect()
            if (item_rect.bottom() < visible_top or item_rect.top() > visible_bottom):
                to_remove.append(idx)
                
        # Remove items outside the culling zone
        for idx in to_remove:
            item = self._image_items.pop(idx)
            self.removeItem(item)
            logger.debug(f"Culled image {idx} (outside viewport)")
            
        # Force garbage collection occasionally when many items are culled
        if len(to_remove) > 5:
            gc.collect()
    
    def add_image(self, index, pixmap, is_placeholder=False):
        """Add a new image to the scene"""
        # If image already exists, replace it
        if index in self._image_items:
            self._image_items[index].setPixmap(pixmap)
            return True
            
        # Check if this is the next image in sequence
        if index != self._cur_index + 1:
            # Queue images that aren't ready to be displayed yet
            self._image_queue.put((index, pixmap, is_placeholder))
            if not self._image_processing:
                self._image_processing = True
                self._image_timer.start(AppConfig.UI.image_loading_intervals())
            return False
        
        # Add the next image in sequence
        item = QGraphicsPixmapItem(pixmap)
        item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        item.setPos(-pixmap.width() // 2, self._cur_y)
        
        self._cur_index = index
        self._cur_y += item.boundingRect().height()
        
        self.addItem(item)
        self._image_items[index] = item
        
        # If not a placeholder, cache the full resolution image
        if not is_placeholder:
            self._image_cache.put(index, pixmap)
            
        # Process any pending images that might now be in sequence
        self._process_image_queue()
        return True
    
    def _process_image_queue(self):
        """Process any pending image operations"""
        if self._image_queue.empty():
            self._image_processing = False
            self._image_timer.stop()
            return
            
        # Get next pending operation
        index, pixmap, is_placeholder = self._image_queue.get()
        
        # If this is the next image in sequence, add it
        if index == self._cur_index + 1:
            self.add_image(index, pixmap, is_placeholder)
        # If image already exists, update it
        elif index in self._image_items:
            self._image_items[index].setPixmap(pixmap)
            if not is_placeholder:
                self._image_cache.put(index, pixmap)
        # Otherwise put it back in the queue if queue isn't too big
        elif self._image_queue.qsize() < 10:
            self._image_queue.put((index, pixmap, is_placeholder))
    
    def clear(self):
        """Clear the scene and reset state"""
        super().clear()
        self._image_items.clear()
        self._image_cache.clear()
        while not self._image_queue.empty():
            try:
                self._image_queue.get_nowait()
            except:
                break
        self._cur_index = -1
        self._cur_y = 0
        self._image_processing = False
        self._image_timer.stop()
        gc.collect()


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
        
        # Set up viewport update timer for culling
        self._viewport_timer = QTimer(self)
        self._viewport_timer.timeout.connect(self._update_viewport_rect)
        self._viewport_timer.start(500)  # Check viewport every 500ms
        
        # Track loaded images to avoid duplicates
        self._loaded_images = set()
        
    def _update_viewport_rect(self):
        """Update the viewport rectangle for culling invisible items"""
        viewport_rect = self.viewport().rect()
        scene_rect = self.mapToScene(viewport_rect).boundingRect()
        self._scene.set_visible_rect(scene_rect)
        
        # Check if we need to preload more images
        self._check_preload_images()
        
    def _check_preload_images(self):
        """Check if we need to preload more images based on scroll position"""
        if not self.chapter:
            return
            
        # Get current scroll position and viewport size
        scrollbar = self.verticalScrollBar()
        max_val = scrollbar.maximum()
        current = scrollbar.value()
        
        # If we're getting close to the bottom, request more images
        if max_val > 0 and current / max_val > 0.7:
            # Find the highest loaded image index
            max_index = max(self._loaded_images) if self._loaded_images else 0
            
            # Request next few images if available
            for i in range(max_index + 1, min(max_index + 5, self.chapter.page_count + 1)):
                if i not in self._loaded_images:
                    self._request_image(i)

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
        """Add a low-resolution placeholder image"""
        # Scale down the placeholder to reduce memory usage
        target_width = int(self._base_width * self._current_scale)
        scaled_pixmap = pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        
        self._scene.add_image(index, scaled_pixmap, is_placeholder=True)
        self._loaded_images.add(index)

    def replace_placeholder(self, index: int, image_data: bytes):
        """Replace a placeholder with the full-resolution image"""
        # Load image from binary data
        img = QImage()
        img.loadFromData(image_data)
        
        # Only scale if needed
        if img.width() > self._base_width:
            target_width = int(self._base_width * self._current_scale)
            pixmap = QPixmap.fromImage(img.scaledToWidth(
                target_width, 
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            pixmap = QPixmap.fromImage(img)
            
        self._scene.add_image(index, pixmap)
        self._loaded_images.add(index)
        
    def _request_image(self, index):
        """Request loading of an image (to be implemented by calling code)"""
        # This method would typically be connected to a callback from the manga loader
        # For now, we just mark it as loaded to prevent duplicate requests
        self._loaded_images.add(index)

    def set_manga(self, manga: Manga):
        self.manga = manga
        self.chapter_selection.clear()
        self.chapter_selection.addItems(
            [f"Chapter {i}" for i in range(1, manga.last_chapter + 1)]
        )

    def set_chapter(self, chapter: MangaChapter):
        self.clear()
        self.chapter = chapter
        self.chapter_selection.setCurrentIndex(chapter.number - 1)
        self._loaded_images.clear()

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

                # Update cached width for future image loading
                self._base_width = 480 / new_scale
                
                event.accept()
            return

        # Update viewport after scrolling
        result = super().wheelEvent(event)
        self._update_viewport_rect()
        return result

    def clear(self):
        """Clear the viewer state and release resources"""
        self.verticalScrollBar().setValue(0)
        if hasattr(self, '_scene') and self._scene:
            self._scene.clear()
        self._loaded_images.clear()
        gc.collect()  # Force garbage collection

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
        self._update_viewport_rect()
