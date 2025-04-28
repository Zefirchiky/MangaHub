from models.manga import MangaState

from .model_json_parser import ModelJsonParser
from config import AppConfig

class StateParser(ModelJsonParser):
    def __init__(self, file: str, state: MangaState):
        super().__init__(AppConfig.Dirs.STATE / file, state)
        
    def get_state(self) -> MangaState:
        return self.get_model()
    
    def save(self, state: MangaState) -> None:
        super().save(state)