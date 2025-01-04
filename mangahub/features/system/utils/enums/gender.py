from enum import Enum, auto


class Gender(Enum):
    MALE = auto()
    FEMALE = auto()
    GENDERLESS = auto()
    HERMAPHRODITE = auto()
    
class Orientation(Enum):
    STRAIGHT = auto()
    LGBT = auto()
    BISEXUAL = auto()
    ASEXUAL = auto()