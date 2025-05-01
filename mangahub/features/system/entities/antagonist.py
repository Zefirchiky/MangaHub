from .entity import Entity


class Antagonist(Entity):
    def __init__(self, name: str = "Antagonist"):
        super().__init__(name)
