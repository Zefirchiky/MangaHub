from pathlib import Path

from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor
from PySide6.QtCore import Qt, QObject, Signal, Property
from loguru import logger



class ImageWidget(QLabel):
    type image_types = Path | str | bytes | bytearray | QPixmap
    
    _default_placeholder = None
    _default_error_image = None
    
    border_radius_changed = Signal(int)
    clicked_r = Signal()
    clicked_l = Signal()
    
    error = Signal(tuple)
    status = Signal(str)
    
    def __init__(self, image_data=None, width=0, height=0, save_original=True, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if not ImageWidget._default_placeholder:
            logger.warning("No default placeholder set, setting standard placeholder...")
            ImageWidget.set_default_placeholder(width=200, height=300)
        if not ImageWidget._default_error_image:
            logger.warning("No default error image set, setting standard error image...")
            ImageWidget.set_default_error_image()

        self.placeholder = self._default_placeholder
        if image_data:
            self.image = self._load_image(image_data)
            self.setPixmap(self.image)
        else:
            self.image = self.placeholder

        if save_original:
            self._original_image = self.image
            
        self.error_image = self._default_error_image
        
        if width and height:
            self.scale_to_fit(width, height)
        elif width:
            self.scale_to_width(width)
        elif height:
            self.scale_to_height(height)
            
        self._border_radius = 5
        self.clickable_left = False
        self.clickable_right = False
        self.save_original = save_original
        
        self.scale(self.placeholder.width(), self.placeholder.height())
        self.update_size()
        
    @staticmethod
    def _process_image(image_data: image_types) -> QPixmap:
        if isinstance(image_data, QPixmap):
            return image_data
        elif isinstance(image_data, Path):
            return QPixmap().fromImage(QImage(str(image_data)))
        elif isinstance(image_data, str):
            return QPixmap().fromImage(QImage(image_data))
        else:
            return QPixmap().fromImage(QImage().fromData(image_data))
    
    def _load_image(self, image_data: image_types) -> QPixmap:
        try:
            return self._process_image(image_data)
        except Exception as e:
            return self._handle_error("Failed to load image", type(e), str(e))
    
    def _handle_error(self, error_message, error_type, error):
        self.error.emit((error_message, error_type, error))
        self.status.emit(f"{error_message}: {error}")
        logger.error(f"{error_message}: {error}")
        self.image = QPixmap(self.error_image)
        self.scale_to_fit(self.width(), self.height())
        return self.image
        
    def set_image(self, image_data: image_types, replace_default_size=False):
        self.image = self._load_image(image_data)
        self.setPixmap(self.image)
        if self.save_original:
            self._original_image = self.image
        if replace_default_size:
            self.set_placeholder(self.image.width(), self.image.height())
            self.setFixedSize(self.image.width(), self.image.height())
        else:
            self.scale_to_fit(self.width(), self.height())
            
        return self
        
    def set_placeholder(self, placeholder: image_types=None, width: int=0, height: int=0, color=(200, 200, 200, 50)):
        if placeholder:
            self.placeholder = self._process_image(placeholder)
            
        elif width and height:
            if not self._default_placeholder:
                self.placeholder = QPixmap(width, height)
                self.placeholder = self.placeholder.fill(QColor(*color))
            else:
                placeholder = self._default_placeholder.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                x = placeholder.width()//2 - width//2 if placeholder.width() > width else 0
                y = placeholder.height()//2 - height//2 if placeholder.height() > height else 0
                self.placeholder = placeholder.copy(x, y, width, height)
            
        else:
            self.placeholder = self._default_placeholder
            
        self.update_size()
        self.update()
        return self.image
        
    def set_error_image(self, error_image: image_types):
        if isinstance(error_image, Path):
            error_image = str(error_image)
        self.error_image = error_image
        
    def set_clickable(self, left=True, right=False):
        self.clickable_left = left
        self.clickable_right = right
        if not left and not right:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def fit(self, width, height, x='auto', y='auto') -> 'ImageWidget':
        if x == 'auto':
            x = self.width()//2
        elif x <= 0:
            x = self.width() - width + x
            
        if y == 'auto':
            y = self.height()//2
        elif y <= 0:
            y = self.height() - height + y
            
        self.image = self.image.copy(x, y, width, height)
        self.setPixmap(self.image)
        self.update_size()
        return self
            
    def scale_to_fit(self, width, height) -> 'ImageWidget':
        if self.original_image:
            self.image = self.original_image
        self.image = self.image.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        self.update_size()
        return self
    
    def scale(self, width, height, aspect_ratio_mode: Qt.AspectRatioMode = Qt.AspectRatioMode.IgnoreAspectRatio) -> 'ImageWidget':
        if self.original_image:
            self.image = self.original_image
        self.image = self.image.scaled(width, height, aspect_ratio_mode, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        self.update_size()
        return self
        
    def scale_to_width(self, width) -> 'ImageWidget':
        if self.original_image:
            self.image = self.original_image
        self.image = self.image.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        self.update_size()
        return self
    
    def scale_to_height(self, height) -> 'ImageWidget':
        if self.original_image:
            self.image = self.original_image
        self.image = self.image.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.image)
        self.update_size()
        return self
    
    def update_size(self):
        self.setFixedSize(self.placeholder.width(), self.placeholder.height())
        return self
        
    @classmethod
    def set_default_placeholder(cls, placeholder_data: image_types=None, width=0, height=0, color=(200, 200, 200, 50)):
        if not placeholder_data:
            placeholder = QPixmap(width, height)
            placeholder.fill(QColor(*color))
        else:
            placeholder = cls._process_image(placeholder_data)
            if width and height:
                placeholder = placeholder.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                x = placeholder.width()//2 - width//2 if placeholder.width() > width else 0
                y = placeholder.height()//2 - height//2 if placeholder.height() > height else 0
                placeholder = placeholder.copy(x, y, width, height)
                
        cls._default_placeholder = placeholder
        return cls._default_placeholder
        
    @classmethod
    def set_default_error_image(cls, error_image: image_types=None):
        if not error_image:
            if cls._default_placeholder:
                error_image = cls._default_placeholder
            else:
                error_image = QPixmap(100, 100)
                error_image.fill(QColor(200, 200, 200, 50))
        else:
            cls._default_error_image = cls._process_image(error_image)
            
        return cls._default_error_image
    
    @property
    def original_image(self) -> QPixmap:
        if self._original_image:
            return self._original_image
        logger.warning("No original image saved")
        return None
    
    @Property(int)
    def border_radius(self):
        return self._border_radius
    
    @border_radius.setter
    def border_radius(self, val):
        min_ = min(self.width()//2, self.height()//2)
        if val > min_:
            logger.warning("Border radius too large, setting to " + str(min_))
            self._border_radius = min_
        if val < 0:
            logger.warning("Border radius is negative, setting to 0")
            self._border_radius = 0
        else:
            self._border_radius = val
        self.update()
    
    def mousePressEvent(self, event):
        if self.clickable_left and event.button() == Qt.MouseButton.LeftButton:
            self.clicked_l.emit()
                
        if self.clickable_right and event.button() == Qt.MouseButton.RightButton:
            self.clicked_r.emit()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rounded_rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rounded_rect, self.border_radius, self.border_radius, Qt.AbsoluteSize)

        painter.setClipPath(path)

        if self.placeholder:
            painter.drawPixmap(self.rect(), self.placeholder)

        if self.image:
            image_rect = self.rect().center() - self.image.rect().center()
            painter.drawPixmap(image_rect, self.image)

        painter.end()
        