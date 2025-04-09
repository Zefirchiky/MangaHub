from directories import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from .smooth_scroll_mixin import SmoothScrollMixin


class SmoothGraphicsView(QGraphicsView, SmoothScrollMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_smooth_scroll()
        self.setObjectName("smooth_graphics_view")
        self.viewport().setObjectName("smooth_graphics_view")
        self.setStyleSheet(f'''
                           #smooth_graphics_view {{
                               border: 1px solid {self.palette().window().color().lighter().name()};
                               border-radius: 5px;
                               background: url({str(BACKGROUNDS_DIR).replace('\\', '/')}/novel_viewer.jpg) repeat;
                            }}''')
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.background_image = QPixmap(str(BACKGROUNDS_DIR/'manga_viewer.jpg').replace('\\', '/'))
        
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
        
    def drawBackground(self, painter: QPainter, rect):
        painter.drawTiledPixmap(rect, self.background_image)