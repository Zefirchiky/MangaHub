import time
import io
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap
from PIL import Image, ImageQt
from loguru import logger

from .strip import StripInfo, StripData
from resources.enums import StripQuality, StorageSize
from utils import ThreadingManager


SCALE_FACTORS = {
            StripQuality.PREVIEW: 0.125,
            StripQuality.LOW: 0.25,
            StripQuality.MEDIUM: 0.5,
            StripQuality.HIGH: 1.0
        }

class StripCache(QObject):
    strip_loaded = Signal(str, int, StripData)
    strip_unloaded = Signal(str, int)
    
    def __init__(self):
        super().__init__()
        self.cache: dict[str, dict[int, StripData]] = {}
        self.current_memory_usage = StorageSize(0)
        
    def request(self, strip_info: StripInfo, quality: StripQuality, image_bytes: bytes) -> QPixmap | None:
        print(strip_info, quality)
        if strip_info.image_name not in self.cache:
            self.cache[strip_info.image_name] = {}
        if strip_info.index not in self.cache[strip_info.image_name]:
            self.cache[strip_info.image_name][strip_info.index] = StripData(
                info=strip_info,
            )
        
        strip_data = self.cache[strip_info.image_name][strip_info.index]
        strip_data.last_accessed = time.time()
        
        # Return cached pixmap if available
        if strip_data.pixmap is not None:
            self.strip_loaded.emit(strip_info.image_name, strip_info.index, strip_data)
        elif strip_data.preview_pixmap is not None:
            self.strip_loaded.emit(strip_info.image_name, strip_info.index, strip_data)
        
        if strip_data.loading_quality != quality:
            strip_data.loading_quality = quality
            self._load_strip_async(strip_info, quality, image_bytes)
    
    def _load_strip_async(self, strip_info: StripInfo, quality: StripQuality, image_bytes: bytes):
        worker = ThreadingManager.run(
            self._load_strip_worker,
            strip_info, quality, image_bytes,
            name=f"strip_load_{strip_info.image_name}_{strip_info.index}_{quality.name}"
        )
        worker.signals.success.connect(
            lambda name, result: self._on_strip_loaded(strip_info, quality, result)
        )
        worker.signals.error.connect(
            lambda name, error: logger.error(f"Strip loading failed: {name}, error: {error}")
        )
        
    def _load_strip_worker(self, strip_info: StripInfo, quality: StripQuality, image_bytes: bytes) -> QPixmap:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        strip = img.crop((
            0, strip_info.y_start,
            strip_info.width, strip_info.y_end
        ))
        
        scale = SCALE_FACTORS[quality]
        if scale < 1.0:
            new_size = (
                int(strip.width * scale),
                int(strip.height * scale)
            )
            strip.thumbnail(new_size, Image.Resampling.LANCZOS)
            strip.save(f'cache/images/strips/{strip_info.image_name}-{strip_info.index}', format='WEBP', effort=1)
        
        return QPixmap.fromImage(ImageQt.ImageQt(strip))
    
    def _on_strip_loaded(self, strip_info: StripInfo, quality: StripQuality, pixmap: QPixmap):
        image_name = strip_info.image_name
        strip_index = strip_info.index
        
        if (image_name in self.cache and 
            strip_index in self.cache[image_name]):
            
            strip_data = self.cache[image_name][strip_index]
            if quality is not StripQuality.PREVIEW:
                strip_data.pixmap = pixmap
            else:
                strip_data.preview_pixmap = pixmap
            strip_data.loaded_quality = quality
            strip_data.loading_quality = None
            
            memory_used = self._estimate_pixmap_memory(pixmap)
            self.current_memory_usage += memory_used
            
            logger.debug(f"Strip loaded: {image_name}[{strip_index}] {quality.name}, "
                        f"memory: {memory_used}, total: {self.current_memory_usage}")
            
            self.strip_loaded.emit(image_name, strip_index, strip_data)
    
    def _estimate_pixmap_memory(self, pixmap: QPixmap) -> int:
        """Estimate memory usage of a pixmap in bytes"""
        if pixmap.isNull():
            return 0
        return pixmap.width() * pixmap.height() * 4
    
    