from models.manga import MangaState

from .model_json_parser import ModelJsonParser
from config import AppConfig


class StateParser(ModelJsonParser[MangaState]):
    def __init__(self, file: str, state: MangaState):
        super().__init__(AppConfig.Dirs.STATE / file, state)
