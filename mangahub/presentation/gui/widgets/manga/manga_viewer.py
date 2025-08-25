from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer, Signal, QRectF, QPointF
from PySide6.QtGui import QPixmap, QFont, QWheelEvent
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
)

from loguru import logger

from presentation.gui.widgets import IconRepo
from presentation.gui.widgets.buttons import IconButton
from presentation.gui.widgets.scroll_areas import SmoothScrollMixin
from services import ContentAwareTileManager
from domain.models.images import ImageMetadata, ImageCache, StripCache
from .manga_image_item import MangaImageItem
from .debug import DebugCapableMixin

from config import Config


class MangaViewer(QGraphicsView, SmoothScrollMixin, DebugCapableMixin):
    def __init__(self, image_cache: ImageCache, parent=None):
        super().__init__(parent)
        self.init_smooth_scroll(vertical=True)

        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setup_debug_monitoring()
        
        self.tile_manager = ContentAwareTileManager()
        self.strip_cache = StripCache()
        self.image_cache = image_cache
        
        self.manga_items: dict[int, MangaImageItem] = {}  # index -> MangaImageItem
        self.image_positions: dict[int, float] = {}       # index -> y_position

        self.images = []
        self.current_zoom = 1.0
        self.fit_to_width = False
        
        self.cull_height_multiplier = Config.Performance.MangaViewer.cull_height_multiplier()
        self.debug_gap = Config.UI.MangaViewer.debug_gap() if Config.debug_mode() else 0

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        logger.success(
            f"MangaViewer initialized with buffer={self.cull_height_multiplier}x, "
            f"debug_gap={self.debug_gap}px"
        )

    def add_manga_image(self, index: int, metadata: ImageMetadata):
        """Add a manga image at specific index (handles out-of-order downloads)"""
        if index in self.manga_items:
            logger.warning(f"Image at index {index} already exists, replacing")
            self._remove_manga_image(index)
        
        # Calculate position based on index and other images
        y_position = self._calculate_position_for_index(index)
        self.image_positions[index] = y_position
        
        # Create manga item
        manga_item = MangaImageItem(
            index, metadata, self.tile_manager, self.strip_cache, self.image_cache
        )
        manga_item.setPos(-metadata.width//2, y_position)
        
        # Scale to fit width if needed
        if self.fit_to_width:
            self._apply_fit_width_scaling(manga_item)
        
        self._scene.addItem(manga_item)
        self.manga_items[index] = manga_item
        
        # Update positions of items that come after this one
        self._recalculate_positions_after(index)
        print(index, y_position, self.image_positions)

        self._update_scene_rect()
        return manga_item
    
    def _calculate_position_for_index(self, index: int) -> float:
        """Calculate Y position for image at given index"""
        y_position = 0.0
        
        # Sum heights of all images that should come before this index
        for i in sorted(self.image_positions.keys()):
            if i >= index:
                break
            
            if i in self.manga_items:
                item = self.manga_items[i]
                y_position += item.metadata.height
                y_position += self.debug_gap  # Add gap if in debug mode
        
        return y_position
    
    def _recalculate_positions_after(self, changed_index: int):
        """Recalculate positions for all items after the changed index"""
        sorted_indices = sorted(self.image_positions.keys())
        
        for index in sorted_indices[changed_index:]:
            new_position = self._calculate_position_for_index(index)
            
            if abs(new_position - self.image_positions[index]) > 1.0:  # Only update if significant change
                self.image_positions[index] = new_position
                if self.manga_items.get(index):
                    self.manga_items[index].setPos(-self.manga_items[index].metadata.width//2, new_position)
    
    def _remove_manga_image(self, index: int):
        """Remove manga image at index"""
        if index in self.manga_items:
            item = self.manga_items[index]
            self._scene.removeItem(item)
            del self.manga_items[index]
            del self.image_positions[index]
    
    def _apply_fit_width_scaling(self, manga_item: MangaImageItem):
        """Apply fit-to-width scaling to a manga item"""
        view_width = self.viewport().width()
        if manga_item.metadata.width > 0 and view_width > 0:
            scale_factor = view_width / manga_item.metadata.width
            manga_item.setScale(scale_factor)

    def wheelEvent(self, event: QWheelEvent):
        modifiers = event.modifiers()

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            self._handle_zoom(event)
        else:
            SmoothScrollMixin.wheelEvent(self, event)
        self._update_visible_strips()

    def _handle_zoom(self, event: QWheelEvent):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15

        old_pos = self.mapToScene(event.pos())
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

        self.current_zoom *= zoom_factor
        self.fit_to_width = False

        event.accept()

    def fit_width(self):
        self.fit_to_width = True
        if self.images:
            # Use middle image for scale calculation
            mid_item = self.manga_items[len(self.manga_items) // 2]
            if mid_item.metadata.width > 0:
                view_width = self.viewport().width()
                scale_factor = view_width / mid_item.metadata.width

                self.resetTransform()
                self.scale(scale_factor, scale_factor)
                self.current_zoom = scale_factor

    def _update_scene_rect(self):
        if not self.manga_items:
            return

        total_height = 0
        max_width = 0

        for item in self.manga_items.values():
            total_height += item.metadata.height
            max_width = max(max_width, item.metadata.width)

            if Config.debug_mode():
                total_height += self.debug_gap

        self.scene().setSceneRect(-max_width//2, 0, max_width, total_height)

    def _update_visible_strips(self):
        """Update strip loading based on current viewport"""
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        
        # Performance monitoring
        if hasattr(self, 'performance_monitor') and self.performance_monitor:
            strips_in_viewport = 0
            strips_in_buffer = 0
            strips_in_preview = 0
            
            for manga_item in self.manga_items.values():
                # Count strips in different zones for monitoring
                for strip in manga_item.strips:
                    strip_rect = QRectF(
                        manga_item.x(),
                        manga_item.y() + strip.y_start,
                        strip.width,
                        strip.height
                    )
                    
                    if strip_rect.intersects(viewport_rect):
                        strips_in_viewport += 1
                    else:
                        distance = manga_item._calculate_distance_to_viewport(
                            QRectF(0, strip.y_start, strip.width, strip.height),
                            manga_item.mapRectFromScene(viewport_rect)
                        )
                        if distance < 500:
                            strips_in_buffer += 1
                        else:
                            strips_in_preview += 1
                
                # Update strip loading for this item
                manga_item.update_viewport_strips(viewport_rect, self.cull_height_multiplier)
            
            self.performance_monitor.update_strip_counts(
                strips_in_viewport, strips_in_buffer, strips_in_preview
            )
        else:
            # Just update strip loading without monitoring
            for manga_item in self.manga_items.values():
                manga_item.update_viewport_strips(viewport_rect, self.cull_height_multiplier)

    def on_metadata_downloaded(self, index: int, metadata: ImageMetadata):
        """Handle metadata_downloaded signal"""
        logger.debug(f"Metadata downloaded for index {index}: {metadata.name} "
                    f"({metadata.width}x{metadata.height})")
        
        if index not in self.manga_items:
            position = self._calculate_position_for_index(index)
            self.image_positions[index] = position
    
    def on_image_downloaded(self, index: int, metadata: ImageMetadata):
        """Handle image_downloaded signal"""
        logger.success(f"Image downloaded for index {index}: {metadata}")
        self.add_manga_image(index, metadata)
        
    def get_current_reading_position(self) -> tuple[int, float]:
        """Get current reading position as (image_index, progress_in_image)"""
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        viewport_center_y = viewport_rect.center().y()
        
        # Find which image the viewport center is in
        for index in sorted(self.image_positions.keys()):
            if index not in self.manga_items:
                continue
                
            item = self.manga_items[index]
            item_start = item.y()
            item_end = item.y() + item.metadata.height
            
            if item_start <= viewport_center_y <= item_end:
                progress = (viewport_center_y - item_start) / item.metadata.height
                return index, progress
        
        # If not in any image, return closest
        if self.manga_items:
            closest_index = min(
                self.image_positions.keys(),
                key=lambda i: abs(self.image_positions[i] - viewport_center_y)
            )
            return closest_index, 0.0
        
        return 0, 0.0
    
    def scroll_to_image(self, index: int, progress: float = 0.0):
        """Scroll to specific image and progress within that image"""
        if index not in self.manga_items:
            logger.warning(f"Cannot scroll to image {index}: not loaded")
            return
        
        item = self.manga_items[index]
        target_y = item.y() + (item.metadata.height * progress)
        
        # Center the target position in viewport
        viewport_height = self.viewport().height()
        scene_point = QPointF(0, target_y - viewport_height / 2)
        self.centerOn(scene_point)
        
        logger.info(f"Scrolled to image[{index}] at {progress:.1%} progress")
        
    def clear(self):
        self.manga_items = {}
        self.image_positions = {}
        self.images = []
        for item in self.scene().items():
            del item