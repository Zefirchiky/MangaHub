from dataclasses import dataclass, field
from typing import List
from .tags.tag import Tag


@dataclass
class ChapterImage:
    number: int
    width: int
    height: int
    image: str = ''
    tags: List[Tag] = field(default_factory=list)
    