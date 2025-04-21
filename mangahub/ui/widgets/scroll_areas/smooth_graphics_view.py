from directories import BACKGROUNDS_DIR
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
                            }}''')
        
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.bg_image = QPixmap(str(BACKGROUNDS_DIR/'manga_viewer.jpg').replace('\\', '/'))
        self.setBackgroundBrush(self.bg_image)
        
        # Optimize rendering
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
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