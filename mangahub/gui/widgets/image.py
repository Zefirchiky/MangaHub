from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QPainter, QPainterPath
from PySide6.QtCore import Qt, QObject, Signal, QRect
from glm import vec2


class ImageSignals(QObject):
    clicked_r = Signal()
    clicked_l = Signal()

class ImageWidget(QLabel):
    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setScaledContents(True)

        self.image = self._load_image(image_data)
        self.original_image = self.image

        self.setPixmap(self.image)
        self.signals = ImageSignals()

        self.border_radius = 5
        self.clickable_left = True
        self.clickable_right = True

    def _load_image(self, image_data):
        if isinstance(image_data, QPixmap):
            return image_data
        elif isinstance(image_data, str):
            return QPixmap().fromImage(QImage(image_data))
        else:
            return QPixmap().fromImage(QImage().fromData(image_data))
        
    def set_clickable(self, left=False, right=False):
        self.clickable_left = left
        self.clickable_right = right
        if not left and not right:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def fit(self, size):
        self.image = self.image.copy(0, 0, *size.xy)
        self.setPixmap(self.image)
        return self
            
    def scale_to_fit(self, size):
        self.image = self.original_image.scaled(*size.xy, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        return self
        
    def scale_to_width(self, width) -> vec2:
        self.image = self.original_image.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        return vec2(self.image.width(), self.image.height())
    
    def scale_to_height(self, height) -> vec2:
        self.image = self.original_image.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        return vec2(self.image.width(), self.image.height())
    
    def mousePressEvent(self, event):
        if self.clickable_left and event.button() == Qt.MouseButton.LeftButton:
            self.signals.clicked_l.emit()
                
        if self.clickable_right and event.button() == Qt.MouseButton.RightButton:
            self.signals.clicked_r.emit()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rounded_rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rounded_rect, self.border_radius, self.border_radius, Qt.SizeMode.AbsoluteSize)
        painter.setClipPath(path)
        
        painter.drawPixmap(rounded_rect, self.image)
        painter.end()