from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem


class MangaStripItem(QGraphicsPixmapItem):
    def __init__(self, parent, pixmap: QPixmap | None=None):
        super().__init__(parent or QPixmap())
        self.setPixmap(pixmap)
        self.setCacheMode(QGraphicsPixmapItem.CacheMode.DeviceCoordinateCache)