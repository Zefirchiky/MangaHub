from PySide6.QtGui import QPixmap
from pydantic import BaseModel, ConfigDict
from resources.enums import StripQuality


class StripInfo(BaseModel):
    image_name: str
    index: int
    y_start: int
    y_end: int
    width: int
    height: int
    is_panel_boundary: bool = False # True if created by content-aware detection
    confidence: float = 0.0
    
    
class StripData(BaseModel):
    """Cached strip data with quality levels"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    info: StripInfo
    preview_pixmap: QPixmap | None = None
    pixmap: QPixmap | None = None
    loaded_quality: StripQuality | None = None
    loading_quality: StripQuality | None = None
    last_accessed: float = 0.0
    
    
class PanelDetectionResult(BaseModel):
    """Result of panel boundary detection"""
    boundaries: list[int]
    confidence: float = 0.0
    method: str = ''
    processing_time_ms: float = 0.0