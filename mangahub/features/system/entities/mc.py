from system import System

from .entity import Entity


class MC(Entity):
    def __init__(self, name: str='MC', system: System=None) -> None:
        super().__init__(name)
        
        # === MC ===
        self.system: System = system