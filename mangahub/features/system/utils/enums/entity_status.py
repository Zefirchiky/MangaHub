from enum import Enum, auto


class EntityStatus(Enum):
    ALIVE = auto()
    DEAD = auto()
    UNCONSCIOUS = auto()
    WOUNDED = auto()
