import time
import io
from PySide6.QtCore import QObject, Signal
import numpy as np
from PIL import Image
from scipy import ndimage
from loguru import logger

from models.images import (
    StripInfo,
    StripData,
    PanelDetectionResult,
    ImageMetadata,
    ImageCache,
)

from utils import ThreadingManager
from config import Config


class ContentAwareTileManager(QObject):
    """Manages tile creation with content-aware and fallback strategies"""

    strips_generated = Signal(str, list)  # image_name, list[StripInfo]

    def __init__(self):
        super().__init__()
        self.min_strip_height = Config.Performance.MangaViewer.min_strip_height()
        self.max_strip_height = Config.Performance.MangaViewer.max_strip_height()
        self.detection_confidence_threshold = (
            Config.Performance.MangaViewer.detection_confidence_threshold()
        )
        self.strip_mode = (
            Config.Performance.MangaViewer.strip_mode()
        )  # "uniform", "content_aware", "adaptive"

    def generate_strips(self, metadata: ImageMetadata):
        return self._create_uniform_strips(metadata)

    def analyze_panel_async(self, metadata: ImageMetadata, img_bytes: bytes):
        """Start background panel analysis"""
        if self.strip_mode in (
            "content_aware",
            "adaptive",
        ):  # TODO: Strip mode setting should be enum
            worker = ThreadingManager.run(
                self._analyze_panel_worker,
                img_bytes,
                name=f"panel_analysis_{metadata.name}",
            )
            worker.signals.success.connect(
                lambda name, result: self._create_context_aware_strips(
                    metadata, result
                    )
                )
            worker.signals.error.connect(
                lambda name, e: logger.error(e)
            )
            return worker
        return None

    def _analyze_panel_worker(
        self, img_bytes: bytes
    ) -> PanelDetectionResult:
        try:
            start_time = time.perf_counter()

            img = Image.open(io.BytesIO(img_bytes))
            img_array = np.array(img.convert("L"))  # Grayscale

            boundaries = []
            confidence = 0
            method = "failed"

            # Edge detection (medium speed, higher accuracy)
            # edge_boundaries = self._detect_panel_edges(img_array)
            # if edge_boundaries and len(edge_boundaries) > len(boundaries):
            #     boundaries = edge_boundaries
            #     confidence = 0.8
            #     method = "edge_detection"

            # White space analysis (fast)
            if confidence < self.detection_confidence_threshold:
                if gutter_boundaries := self._find_gutter(img_array):  # TODO: Optimize
                    boundaries = gutter_boundaries
                    confidence = 0.7
                    method = "gutter_detection"

            processing_time = time.perf_counter() - start_time
            result = PanelDetectionResult(
                boundaries=boundaries,
                confidence=confidence,
                method=method,
                processing_time_ms=processing_time
            )

            return result

        except Exception as e:
            return PanelDetectionResult([], 0.0, f"error: {str(e)}")

    def _find_gutter(self, img_array: np.ndarray) -> list[int]:
        """Find horizontal gutters (white space between panels)"""
        dt = time.perf_counter()
        height, width = img_array.shape

        row_scores = []
        for y in range(height):
            row = img_array[y]
            # Consider pixels > 240 as background (white/light)
            background_ratio = np.sum(row > 240) / width
            row_scores.append(background_ratio)

        # Find regions with high background ratio
        gutter_threshold = (
            Config.Performance.MangaViewer.gutter_threshold()
        )  # e.g., 0.8
        min_gutter_height = (
            Config.Performance.MangaViewer.min_gutter_height()
        )  # e.g., 10px

        gutters = []
        in_gutter = False
        gutter_start = 0

        for y, score in enumerate(row_scores):
            if score > gutter_threshold and not in_gutter:
                in_gutter = True
                gutter_start = y
            elif score <= gutter_threshold and in_gutter:
                gutter_height = y - gutter_start
                if gutter_height >= min_gutter_height:
                    # Use middle of gutter as cut point
                    gutters.append(gutter_start + gutter_height // 2)
                in_gutter = False
                
        return gutters

    def _detect_panel_edges(self, img_array: np.ndarray) -> list[int]:
        """Detect panel boundaries using edge detection"""
        try:
            # Horizontal Sobel filter to detect horizontal edges
            sobel_h = ndimage.sobel(img_array, axis=0)

            # Find strong horizontal edges
            edge_strength = np.abs(sobel_h)
            row_edge_strength = np.mean(edge_strength, axis=1)

            # Find peaks in edge strength
            threshold = np.percentile(row_edge_strength, 90)  # Top 10% of edges
            potential_boundaries = []

            for y in range(len(row_edge_strength)):
                if row_edge_strength[y] > threshold:
                    potential_boundaries.append(y)

            # Group nearby boundaries and take the strongest one from each group
            if not potential_boundaries:
                return []

            grouped_boundaries = []
            current_group = [potential_boundaries[0]]

            for boundary in potential_boundaries[1:]:
                if boundary - current_group[-1] < self.min_strip_height // 2:
                    current_group.append(boundary)
                else:
                    # Find strongest edge in current group
                    best_y = max(current_group, key=lambda y: row_edge_strength[y])
                    grouped_boundaries.append(best_y)
                    current_group = [boundary]

            # Don't forget the last group
            if current_group:
                best_y = max(current_group, key=lambda y: row_edge_strength[y])
                grouped_boundaries.append(best_y)

            return grouped_boundaries

        except Exception as e:
            logger.error(f'Error while detecting panel edges: {e}')
            return []

    def _create_uniform_strips(self, metadata: ImageMetadata) -> list[StripInfo]:
        """Create uniform horizontal strips"""
        strips = []
        strip_height = Config.Performance.MangaViewer.default_strip_height()

        y = 0
        strip_index = 0
        while y < metadata.height:
            end_y = min(y + strip_height, metadata.height)

            strip = StripInfo(
                image_name=metadata.name,
                index=strip_index,
                y_start=y,
                y_end=end_y,
                width=metadata.width,
                height=end_y - y,
                is_panel_boundary=(y == 0 or y == metadata.height - strip_height),
            )
            strips.append(strip)

            y = end_y
            strip_index += 1
            
        return strips

    def _create_context_aware_strips(
        self, metadata: ImageMetadata, result: PanelDetectionResult
    ):
        """Create strips based on panel detection results"""
        if result.confidence < self.detection_confidence_threshold:
            return self._create_uniform_strips(metadata)

        if Config.debug_mode():
            logger.info(
                f"Panel analysis complete for {metadata.name}: "
                f"{len(result.boundaries)} boundaries, "
                f"confidence={result.confidence:.2f}, "
                f"method={result.method}, "
                f"time={result.processing_time_ms}"
            )
            
        strips: list[StripInfo] = []
        strip_index = 0
        boundaries = [0] + result.boundaries + [metadata.height]

        for i in range(len(boundaries) - 1):
            y_start = boundaries[i]
            y_end = boundaries[i + 1]
            height = y_end - y_start

            # Split very large panels into multiple strips
            if height > self.max_strip_height:
                # Split large panel into sub-strips
                sub_strips = self._split_large_strip(
                    metadata.name, strip_index, y_start, y_end, metadata.width
                )
                strips.extend(sub_strips)
                strip_index += len(sub_strips)
            elif height < self.min_strip_height:
            # Merge small strips
                if strips:
                    last_strip = strips[-1]
                    last_strip.y_end = y_end
                    last_strip.height = last_strip.y_end - last_strip.y_start
                else:
                    strip = StripInfo(
                        image_name=metadata.name,
                        index=strip_index,
                        y_start=y_start,
                        y_end=y_end,
                        width=metadata.width,
                        height=height,
                        is_panel_boundary=(i == 0 or y_end == metadata.height),
                        confidence=result.confidence,
                    )
                    strips.append(strip)
                    strip_index += 1
            else:
                strip = StripInfo(
                    image_name=metadata.name,
                    index=strip_index,
                    y_start=y_start,
                    y_end=y_end,
                    width=metadata.width,
                    height=height,
                    is_panel_boundary=(i == 0 or y_end == metadata.height),
                    confidence=result.confidence,
                )
                strips.append(strip)
                strip_index += 1

        self.strips_generated.emit(metadata.name, strips)

    def _split_large_strip(
        self, image_name: str, start_index: int, y_start: int, y_end: int, width: int
    ) -> list[StripInfo]:
        """Split a large strip into smaller ones"""
        strips = []
        current_y = y_start
        strip_index = start_index

        while current_y < y_end:
            next_y = min(current_y + self.max_strip_height, y_end)

            strip = StripInfo(
                image_name=image_name,
                index=strip_index,
                y_start=current_y,
                y_end=next_y,
                width=width,
                height=next_y - current_y,
                is_panel_boundary=False,  # This is a sub-strip
                confidence=0.5,
            )
            strips.append(strip)

            current_y = next_y
            strip_index += 1

        return strips
