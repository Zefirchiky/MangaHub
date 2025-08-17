from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from PySide6.QtCore import QObject, QRectF, QTimer, Signal, QPointF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem

from config import Config
from resources.enums import SU


class PerformanceMetrics(BaseModel):
    """Performance metrics tracked over time"""
    
    # Memory metrics
    total_memory_used: int = 0  # bytes
    memory_by_quality: dict[str, int] = field(default_factory=dict)  # quality -> bytes
    cache_hit_rate: float = 0.0
    cache_miss_count: int = 0
    cache_hit_count: int = 0
    
    # Loading metrics  
    strips_loading: int = 0
    strips_loaded_total: int = 0
    average_load_time_ms: float = 0.0
    load_times: list[float] = field(default_factory=list)  # Recent load times for averaging
    
    # Panel detection metrics
    panel_detections_completed: int = 0
    average_detection_time_ms: float = 0.0
    detection_success_rate: float = 0.0
    detection_method_usage: dict[str, int] = field(default_factory=dict)
    
    # Viewport metrics  
    strips_in_viewport: int = 0
    strips_in_buffer: int = 0
    strips_in_preview: int = 0
    viewport_updates_per_second: float = 0.0
    
    # Threading metrics
    active_workers: int = 0
    queued_workers: int = 0
    completed_workers: int = 0
    worker_types_active: dict[str, int] = field(default_factory=dict)
    
    def add_load_time(self, time_ms: float):
        """Add a new load time and update average"""
        self.load_times.append(time_ms)
        # Keep only recent 50 measurements
        if len(self.load_times) > 50:
            self.load_times = self.load_times[-50:]
        self.average_load_time_ms = sum(self.load_times) / len(self.load_times)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hit_count += 1
        self._update_hit_rate()
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_miss_count += 1
        self._update_hit_rate()
    
    def _update_hit_rate(self):
        """Update cache hit rate"""
        total = self.cache_hit_count + self.cache_miss_count
        if total > 0:
            self.cache_hit_rate = self.cache_hit_count / total


class PerformanceMonitor(QObject):
    """Monitors and tracks performance metrics"""
    
    metrics_updated = Signal(PerformanceMetrics)
    
    def __init__(self):
        super().__init__()
        self.metrics = PerformanceMetrics()
        self.enabled = Config.debug_mode()
        
        # Timing tracking
        self.load_start_times: dict[str, float] = {}  # worker_name -> start_time
        self.detection_start_times: dict[str, float] = {}
        self.viewport_update_times: list[float] = []
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._emit_metrics)
        if self.enabled:
            self.update_timer.start(1000)  # Update every second
    
    def record_strip_load_start(self, worker_name: str):
        """Record start of strip loading"""
        if not self.enabled:
            return
        self.load_start_times[worker_name] = time.time() * 1000
        self.metrics.strips_loading += 1
        logger.debug(f"Strip load started: {worker_name}")
    
    def record_strip_load_complete(self, worker_name: str, success: bool = True):
        """Record completion of strip loading"""
        if not self.enabled:
            return
            
        if worker_name in self.load_start_times:
            load_time = time.time() * 1000 - self.load_start_times[worker_name]
            self.metrics.add_load_time(load_time)
            del self.load_start_times[worker_name]
            
            if success:
                self.metrics.strips_loaded_total += 1
                logger.debug(f"Strip loaded in {load_time:.1f}ms: {worker_name}")
            else:
                logger.warning(f"Strip load failed after {load_time:.1f}ms: {worker_name}")
        
        self.metrics.strips_loading = max(0, self.metrics.strips_loading - 1)
    
    def record_panel_detection_start(self, image_name: str):
        """Record start of panel detection"""
        if not self.enabled:
            return
        self.detection_start_times[image_name] = time.time() * 1000
        logger.debug(f"Panel detection started: {image_name}")
    
    def record_panel_detection_complete(self, image_name: str, method: str, 
                                      confidence: float, success: bool = True):
        """Record completion of panel detection"""
        if not self.enabled:
            return
            
        if image_name in self.detection_start_times:
            detection_time = time.time() * 1000 - self.detection_start_times[image_name]
            
            # Update detection metrics
            self.metrics.panel_detections_completed += 1
            
            # Update average detection time
            if hasattr(self.metrics, '_detection_times'):
                self.metrics._detection_times.append(detection_time)
            else:
                self.metrics._detection_times = [detection_time]
            
            # Keep only recent 20 measurements
            if len(self.metrics._detection_times) > 20:
                self.metrics._detection_times = self.metrics._detection_times[-20:]
            
            self.metrics.average_detection_time_ms = sum(self.metrics._detection_times) / len(self.metrics._detection_times)
            
            # Track method usage
            if method not in self.metrics.detection_method_usage:
                self.metrics.detection_method_usage[method] = 0
            self.metrics.detection_method_usage[method] += 1
            
            # Update success rate
            if hasattr(self.metrics, '_detection_successes'):
                self.metrics._detection_successes.append(success and confidence > 0.5)
            else:
                self.metrics._detection_successes = [success and confidence > 0.5]
            
            if len(self.metrics._detection_successes) > 20:
                self.metrics._detection_successes = self.metrics._detection_successes[-20:]
            
            successes = sum(self.metrics._detection_successes)
            self.metrics.detection_success_rate = successes / len(self.metrics._detection_successes)
            
            del self.detection_start_times[image_name]
            
            logger.info(f"Panel detection completed in {detection_time:.1f}ms: {image_name}, "
                      f"method={method}, confidence={confidence:.2f}, success={success}")
    
    def record_viewport_update(self):
        """Record viewport update for FPS calculation"""
        if not self.enabled:
            return
            
        current_time = time.time()
        self.viewport_update_times.append(current_time)
        
        # Keep only last second of updates
        cutoff_time = current_time - 1.0
        self.viewport_update_times = [t for t in self.viewport_update_times if t > cutoff_time]
        
        self.metrics.viewport_updates_per_second = len(self.viewport_update_times)
    
    def update_memory_usage(self, total_bytes: int, by_quality: dict[str, int]):
        """Update memory usage metrics"""
        if not self.enabled:
            return
            
        self.metrics.total_memory_used = total_bytes
        self.metrics.memory_by_quality = by_quality.copy()
        
        # Log significant memory changes
        memory_mb = total_bytes / (1024 * 1024)
        if memory_mb > 100:  # Log if over 100MB
            logger.info(f"Memory usage: {memory_mb:.1f}MB, by quality: {by_quality}")
    
    def update_strip_counts(self, in_viewport: int, in_buffer: int, in_preview: int):
        """Update strip count metrics"""
        if not self.enabled:
            return
            
        self.metrics.strips_in_viewport = in_viewport
        self.metrics.strips_in_buffer = in_buffer  
        self.metrics.strips_in_preview = in_preview
    
    def update_worker_counts(self, active: int, queued: int, by_type: dict[str, int]):
        """Update thread worker metrics"""
        if not self.enabled:
            return
            
        self.metrics.active_workers = active
        self.metrics.queued_workers = queued
        self.metrics.worker_types_active = by_type.copy()
    
    def _emit_metrics(self):
        """Emit current metrics"""
        if self.enabled:
            self.metrics_updated.emit(self.metrics)


class DebugOverlay(QGraphicsItem):
    """Debug visualization overlay for manga viewer"""
    
    def __init__(self, viewer_widget):
        super().__init__()
        self.viewer = viewer_widget
        self.metrics: Optional[PerformanceMetrics] = None
        self.show_strip_boundaries = True
        self.show_quality_indicators = True
        self.show_performance_overlay = True
        self.show_memory_usage = True
        
        # Visual settings
        self.strip_boundary_pen = QPen(QColor(255, 0, 0, 128), 1)  # Semi-transparent red
        self.panel_boundary_pen = QPen(QColor(0, 255, 0, 180), 2)  # More visible green
        self.quality_colors = {
            'PREVIEW': QColor(255, 0, 0, 80),    # Red
            'LOW': QColor(255, 165, 0, 80),      # Orange  
            'MEDIUM': QColor(255, 255, 0, 80),   # Yellow
            'HIGH': QColor(0, 255, 0, 80)        # Green
        }
        
        self.info_font = QFont("Consolas", 8)
        self.overlay_font = QFont("Consolas", 10, QFont.Weight.Bold)
        
        # Info panel background
        self.info_background = QBrush(QColor(0, 0, 0, 180))
        
    def update_metrics(self, metrics: PerformanceMetrics):
        """Update metrics for display"""
        self.metrics = metrics
        self.update()
    
    def boundingRect(self) -> QRectF:
        """Return bounding rectangle (entire viewport)"""
        if hasattr(self.viewer, 'viewport'):
            viewport_rect = self.viewer.mapToScene(self.viewer.viewport().rect()).boundingRect()
            return viewport_rect
        return QRectF(0, 0, 800, 600)
    
    def paint(self, painter: QPainter, option, widget):
        """Paint debug visualization"""
        if not Config.debug_mode():
            return
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw strip boundaries and quality indicators
        if self.show_strip_boundaries or self.show_quality_indicators:
            self._draw_strip_info(painter)
        
        # Draw performance overlay
        if self.show_performance_overlay and self.metrics:
            self._draw_performance_overlay(painter)
        
        # Draw memory usage
        if self.show_memory_usage and self.metrics:
            self._draw_memory_overlay(painter)
    
    def _draw_strip_info(self, painter: QPainter):
        """Draw strip boundaries and quality information"""
        viewport_rect = self.boundingRect()
        
        for manga_item in self.viewer.manga_items.values():
            item_rect = manga_item.boundingRect()
            
            # Only draw for visible items
            if not item_rect.intersects(viewport_rect):
                continue
                
            for strip in manga_item.strips:
                strip_rect = QRectF(
                    manga_item.x(),
                    manga_item.y() + strip.y_start,
                    strip.width,
                    strip.height
                )
                
                # Skip if strip not in viewport
                if not strip_rect.intersects(viewport_rect):
                    continue
                
                # Draw strip boundary
                if self.show_strip_boundaries:
                    pen = self.panel_boundary_pen if strip.is_panel_boundary else self.strip_boundary_pen
                    painter.setPen(pen)
                    painter.drawRect(strip_rect)
                    
                    # Draw strip index
                    painter.setPen(QPen(QColor(255, 255, 255, 200)))
                    painter.setFont(self.info_font)
                    painter.drawText(
                        strip_rect.topLeft() + QPointF(5, 15),
                        f"S{strip.index}"
                    )
                    
                    # Draw confidence for content-aware strips
                    if strip.is_panel_boundary and strip.confidence > 0:
                        painter.drawText(
                            strip_rect.topLeft() + QPointF(5, 30),
                            f"C{strip.confidence:.2f}"
                        )
                
                # Draw quality indicator
                if self.show_quality_indicators:
                    quality = self._get_strip_quality(strip, viewport_rect)
                    if quality in self.quality_colors:
                        painter.fillRect(
                            QRectF(strip_rect.right() - 20, strip_rect.top(), 15, 15),
                            self.quality_colors[quality]
                        )
                        
                        # Draw quality text
                        painter.setPen(QPen(QColor(0, 0, 0, 255)))
                        painter.setFont(self.info_font)
                        painter.drawText(
                            QPointF(strip_rect.right() - 18, strip_rect.top() + 12),
                            quality[0]  # First letter of quality
                        )
    
    def _get_strip_quality(self, strip, viewport_rect) -> str:
        """Determine current quality level of a strip"""
        # This would need access to strip cache to get actual quality
        # For now, estimate based on distance from viewport
        strip_rect = QRectF(0, strip.y_start, strip.width, strip.height)
        
        if strip_rect.intersects(viewport_rect):
            return "HIGH"
        
        # Calculate distance (simplified)
        distance = abs(strip_rect.center().y() - viewport_rect.center().y())
        if distance < viewport_rect.height():
            return "MEDIUM"
        elif distance < viewport_rect.height() * 2:
            return "LOW"
        else:
            return "PREVIEW"
    
    def _draw_performance_overlay(self, painter: QPainter):
        """Draw performance metrics overlay"""
        viewport_rect = self.boundingRect()
        overlay_rect = QRectF(
            viewport_rect.right() - 250,
            viewport_rect.top() + 10,
            240,
            200
        )
        
        # Background
        painter.fillRect(overlay_rect, self.info_background)
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.drawRect(overlay_rect)
        
        # Performance text
        painter.setFont(self.overlay_font)
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        
        y_offset = overlay_rect.top() + 20
        line_height = 14
        
        perf_lines = [
            "=== PERFORMANCE ===",
            f"Strips Loading: {self.metrics.strips_loading}",
            f"Strips Loaded: {self.metrics.strips_loaded_total}",
            f"Avg Load Time: {self.metrics.average_load_time_ms:.1f}ms",
            f"Cache Hit Rate: {self.metrics.cache_hit_rate:.1%}",
            f"",
            f"Panel Detections: {self.metrics.panel_detections_completed}",
            f"Detection Success: {self.metrics.detection_success_rate:.1%}",
            f"Avg Detection: {self.metrics.average_detection_time_ms:.1f}ms",
            f"",
            f"Viewport FPS: {self.metrics.viewport_updates_per_second:.1f}",
            f"Active Workers: {self.metrics.active_workers}",
            f"Queued Workers: {self.metrics.queued_workers}",
        ]
        
        for line in perf_lines:
            if line:  # Skip empty lines for spacing
                painter.drawText(QPointF(overlay_rect.left() + 10, y_offset), line)
            y_offset += line_height
    
    def _draw_memory_overlay(self, painter: QPainter):
        """Draw memory usage overlay"""
        viewport_rect = self.boundingRect()
        memory_rect = QRectF(
            viewport_rect.left() + 10,
            viewport_rect.top() + 10,
            200,
            120
        )
        
        # Background
        painter.fillRect(memory_rect, self.info_background)
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.drawRect(memory_rect)
        
        # Memory text
        painter.setFont(self.overlay_font)
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        
        total_mb = self.metrics.total_memory_used / (1024 * 1024)
        memory_limit_mb = 100
        usage_percent = (total_mb / memory_limit_mb) * 100 if memory_limit_mb > 0 else 0
        
        y_offset = memory_rect.top() + 20
        line_height = 14
        
        memory_lines = [
            "=== MEMORY ===",
            f"Total: {total_mb:.1f}MB",
            f"Limit: {memory_limit_mb}MB",
            f"Usage: {usage_percent:.1f}%",
            "",
            "By Quality:",
        ]
        
        for line in memory_lines:
            if line:
                painter.drawText(QPointF(memory_rect.left() + 10, y_offset), line)
            y_offset += line_height
        
        # Memory by quality
        for quality, bytes_used in self.metrics.memory_by_quality.items():
            mb_used = bytes_used / (1024 * 1024)
            color = self.quality_colors.get(quality, QColor(255, 255, 255))
            
            # Draw color indicator
            painter.fillRect(
                QRectF(memory_rect.left() + 15, y_offset - 10, 10, 10),
                QBrush(color)
            )
            
            # Draw text
            painter.drawText(
                QPointF(memory_rect.left() + 30, y_offset),
                f"{quality}: {mb_used:.1f}MB"
            )
            y_offset += line_height


class StripDebugItem(QGraphicsRectItem):
    """Individual debug item for strip visualization"""
    
    def __init__(self, strip_info, quality_level="UNKNOWN"):
        super().__init__()
        self.strip_info = strip_info
        self.quality_level = quality_level
        
        # Set rectangle
        self.setRect(0, strip_info.y_start, strip_info.width, strip_info.height)
        
        # Set visual style based on strip type
        if strip_info.is_panel_boundary:
            self.setPen(QPen(QColor(0, 255, 0, 180), 2))  # Green for panel boundaries
        else:
            self.setPen(QPen(QColor(255, 0, 0, 100), 1))  # Red for uniform strips
        
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        
        # Add text item for info
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(f"S{strip_info.index}")
        self.text_item.setPos(5, strip_info.y_start + 5)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255, 200))
        
        font = QFont("Consolas", 8)
        self.text_item.setFont(font)


# Integration helper for adding debug capabilities to existing components
class DebugCapableMixin:
    """Mixin to add debug capabilities to manga viewer components"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.debug_overlay: Optional[DebugOverlay] = None
        
        if Config.debug_mode():
            self.setup_debug_monitoring()
    
    def setup_debug_monitoring(self):
        """Setup debug monitoring and visualization"""
        self.performance_monitor = PerformanceMonitor()
        
        if hasattr(self, 'scene'):  # For QGraphicsView
            self.debug_overlay = DebugOverlay(self)
            self.scene().addItem(self.debug_overlay)
            
            # Connect metrics updates
            self.performance_monitor.metrics_updated.connect(
                self.debug_overlay.update_metrics
            )
    
    def log_performance_event(self, event_type: str, **kwargs):
        """Log a performance event"""
        if self.performance_monitor:
            method_name = f"record_{event_type}"
            if hasattr(self.performance_monitor, method_name):
                method = getattr(self.performance_monitor, method_name)
                method(**kwargs)
            else:
                logger.warning(f"Unknown performance event type: {event_type}")
