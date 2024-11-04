from dataclasses import dataclass
from typing import Any

@dataclass
class BaseModel:
    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
