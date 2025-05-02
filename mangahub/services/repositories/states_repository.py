from __future__ import annotations

from ..parsers.model_json_parser import ModelJsonParser
from config import AppConfig

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.manga import MangaState


class StateRepository(ModelJsonParser['MangaState']):
    def __init__(self, file: str, state: MangaState):
        super().__init__(AppConfig.Dirs.STATE / file, state)
