from enum import Enum, auto


class StripQuality(Enum):
    PREVIEW = auto()    # 12.5% - Far from viewport
    LOW = auto()        # 25% - Near viewport  
    MEDIUM = auto()     # 50% - Buffer zone
    HIGH = auto()       # 100% - Viewport