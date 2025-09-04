import typing
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
    is_panel_boundary: bool = False  # True if created by content-aware detection
    confidence: float = 0.0

    def __eq__(self, other: typing.Self) -> bool:
        return all(
            [self.image_name == other.image_name,
            self.index == other.index,
            self.y_start == other.y_start,
            self.y_end == other.y_end,
            self.width == other.width,
            self.height == other.height,
            self.is_panel_boundary == other.is_panel_boundary,
            self.confidence == other.confidence]
        )


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
    method: str = ""
    processing_time_ms: float = 0.0
