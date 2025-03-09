from directories import STATE_DIR
from models.manga import MangaState

from .model_json_parser import ModelJsonParser


class StateParser(ModelJsonParser):
    def __init__(self, file: str, state: MangaState):
        super().__init__(STATE_DIR / file, state)
        
    def get_state(self) -> MangaState:
        return self.get_model()
    
    def save(self, state: MangaState) -> None:
        super().save(state)