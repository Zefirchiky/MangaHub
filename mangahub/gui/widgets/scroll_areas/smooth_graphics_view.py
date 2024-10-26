from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from .smooth_scroll_mixin import SmoothScrollMixin


class SmoothGraphicsView(QGraphicsView, SmoothScrollMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_smooth_scroll()
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Optimize rendering
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        
        # Viewport behavior
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
    def wheelEvent(self, event):
        SmoothScrollMixin.wheelEvent(self, event)