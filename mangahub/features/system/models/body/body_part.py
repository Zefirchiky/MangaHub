from abc import ABC, abstractmethod


class BodyPart(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hp = 0
        
    def damaged(self, damage: int) -> 'BodyPart':
        self.hp -= damage
        return self