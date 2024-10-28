from dataclasses import dataclass
from typing import Any

@dataclass
class BaseModel:
    """Base model class with common functionality"""
    def update(self, **kwargs: Any) -> None:
        """Update multiple attributes at once"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
