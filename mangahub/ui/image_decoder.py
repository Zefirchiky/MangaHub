import traceback
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage

from models.images import ImageCache
from utils import ThreadingManager, Worker


class ImageDecoderSignals(QObject):
    image_decoded = Signal(str, QPixmap)
    decoding_failed = Signal(str, str)
    decoding_error = Signal(str, tuple)
    
class ImageDecoder(QObject):
    signals = ImageDecoderSignals()
    
    def __init__(self, cache: ImageCache):
        super().__init__()
        self.cache = cache
    
    def decode(self, name: str) -> Worker:
        if not (image := self.cache.get(name)):
            self.signals.decoding_failed.emit(name, f'No image {name} in cache {self.cache}')
        return ThreadingManager.run(self._decode_from_bytes_thread, name, image)
        
    @classmethod
    def decode_from_cache(cls, cache: ImageCache, name: str) -> Worker:
        if not (image := cache.get(name)):
            cls.signals.decoding_failed.emit(name, f'No image {name} in cache {cache}')
        return ThreadingManager.run(cls._decode_from_bytes_thread, name, image)
        
    @classmethod
    def decode_from_bytes(cls, image: bytes, name: str) -> Worker:
        return ThreadingManager.run(cls._decode_from_bytes_thread, name, image)
    
    @classmethod
    def _decode_from_bytes_thread(cls, name: str, image: bytes):
        try:
            cls.signals.image_decoded.emit(name, QPixmap.fromImage(QImage.fromData(image)))
        except Exception as e:
            cls.signals.decoding_failed.emit(name, (type(e), str(e), traceback.format_exc()))