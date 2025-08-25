from __future__ import annotations

from application.services.parsers import ModelJsonParser
from config import Config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from domain.models.manga import MangaState


class StateRepository(ModelJsonParser['MangaState']):
    def __init__(self, file: str, state: MangaState):
        super().__init__(Config.Dirs.STATE / file, state)
