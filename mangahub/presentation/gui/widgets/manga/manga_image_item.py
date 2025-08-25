import math
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsRectItem
from loguru import logger

from presentation.gui import ImageDecoder
from domain.models.images import ImageMetadata, ImageCache, StripInfo, StripData, StripCache
from services import ContentAwareTileManager
from .manga_strip_item import MangaStripItem

from resources.enums import StripQuality
from config import Config


class MangaImageItem(QGraphicsRectItem):
    """Custom graphics item for manga images with strip-based rendering"""

    def __init__(
        self,
        index: int,
        metadata: ImageMetadata,
        tile_manager: ContentAwareTileManager,
        strip_cache: StripCache,
        image_cache: ImageCache,
        parent=None,
    ):
        super().__init__(parent)
        self.index = index
        self.metadata = metadata
        self.tile_manager = tile_manager
        self.strip_cache = strip_cache
        self.image_cache = image_cache
        self.image_decoder = ImageDecoder(image_cache)

        self.strips = []
        self.strip_items: dict[int, MangaStripItem] = {}

        if metadata.width > 0 and metadata.height > 0:
            placeholder = QPixmap(metadata.width, metadata.height)
            placeholder.fill(Qt.GlobalColor.darkGray)

        # Generate initial strips
        # self.strips = tile_manager.generate_strips(metadata)
        # self._create_strip_items()
        
        # tile_manager.strips_generated.connect(self._on_strips_generated)
        # strip_cache.strip_loaded.connect(self._on_strip_loaded)
        
        # tile_manager.analyze_panel_async(metadata, image_cache.get(metadata.name))
    
    def _create_strip_items(self):
        """Create graphics items for each strip"""
        for strip in self.strips:
            strip_item = MangaStripItem(self)
            strip_item.setPos(0, strip.y_start) # -strip.width//2
            self.strip_items[strip.index] = strip_item

    def _on_strips_generated(self, image_name: str, strips: list[StripInfo]):
        if image_name != self.metadata.name:
            return
        self._transition_to_strips(strips)

    def _transition_to_strips(self, new_strips: list[StripInfo]):
        """Transition from uniform to content-aware strips"""
        logger.debug(f"Transitioning to {len(new_strips)} content-aware strips")

        self.strips = new_strips

        # Remove old strip items
        for strip_item in self.strip_items.values():
            strip_item.setParentItem(None)
        self.strip_items.clear()

        # Create new strip items
        self._create_strip_items()
        self.setPixmap(QPixmap(self.pixmap().size()))

    def _on_strip_loaded(self, image_name: str, strip_index: int, strip: StripData):
        """Handle strip loading completion"""
        if image_name != self.metadata.name:
            return

        print('Strip loaded', image_name, strip)
        if strip_index in self.strip_items:
            strip_info = next((s for s in self.strips if s.index == strip_index), None)
            if strip_info:
                pixmap = strip.pixmap
                if pixmap:
                    self.strip_items[strip_index].setPixmap(pixmap)

    def update_viewport_strips(self, viewport_rect: QRectF, buffer_multiplier: float):
        """Update strip loading based on viewport"""
        if not self.strips:
            return

        # Calculate expanded viewport with buffer
        buffer_height = viewport_rect.height() * buffer_multiplier
        expanded_rect = QRectF(
            viewport_rect.x(),
            viewport_rect.y() - buffer_height,
            viewport_rect.width(),
            viewport_rect.height() + 2 * buffer_height,
        )

        for strip in self.strips:
            strip_rect = QRectF(-strip.width//2, strip.y_start, strip.width, strip.height)

            # Determine required quality based on distance from viewport
            distance_from_viewport = self._calculate_distance_to_viewport(
                strip_rect, self.mapRectFromScene(expanded_rect)
            )

            required_quality = self._calculate_required_quality(distance_from_viewport)

            # Request strip at required quality
            self.strip_cache.request(
                strip, required_quality, self.image_cache.get(self.metadata.name)
            )

    def _calculate_distance_to_viewport(
        self, strip_rect: QRectF, viewport_rect: QRectF
    ) -> float:
        """Calculate distance from strip to viewport"""
        if strip_rect.intersects(viewport_rect):
            return 0.0

        dx = max(
            0,
            max(
                strip_rect.left() - viewport_rect.right(),
                viewport_rect.left() - strip_rect.right(),
            ),
        )
        dy = max(
            0,
            max(
                strip_rect.top() - viewport_rect.bottom(),
                viewport_rect.top() - strip_rect.bottom(),
            ),
        )

        return math.sqrt(dx * dx + dy * dy)

    def _calculate_required_quality(self, distance: float) -> StripQuality:
        """Calculate required quality based on distance from viewport"""
        if distance == 0:
            return StripQuality.HIGH
        elif distance < 500:
            return StripQuality.MEDIUM
        elif distance < 1000:
            return StripQuality.LOW
        else:
            return StripQuality.PREVIEW
