from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Tag:
    name: str
    color: str