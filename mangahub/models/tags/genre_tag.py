from ..manga import Manga
from .tag import Tag
from dataclasses import dataclass, field
from typing import List


@dataclass
class GenreTag(Tag):
    manga: List[Manga] = field(default_factory=list)