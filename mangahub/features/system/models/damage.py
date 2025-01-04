from typing import Union
from .defense import Defense
from ..utils.enums import DamageTypes, CustomDamageType


class Damage:
    def __init__(
            self, damage: int, type: DamageTypes | CustomDamageType=DamageTypes.NORMAL, 
            min_: int=0, max_: int=-1
        ) -> None:
        self.damage = damage
        self.type = type
        self.min_ = min_
        self.max_ = max_
        
    def get_damage(self, hp: int=0, defense: list[Defense]=[Defense()]) -> int:     # FIXME: May cause error
        damage_dealt = 0
        if DamageTypes.NORMAL in self.type:
            damage_dealt += self.damage
        if DamageTypes.TRUE in self.type:
            damage_dealt += self.damage
        if DamageTypes.PERCENTAGE in self.type:
            damage_dealt += hp / 100 * self.damage
        for def_ in defense:
            damage_dealt = def_.get_damage(damage_dealt, self.type)
        return damage_dealt
        
    def __add__(self, other: Union[int, float, 'Damage', DamageTypes]) -> 'Damage':
        if isinstance(other, int) or isinstance(other, float):
            self.damage += other
        elif isinstance(other, Damage):
            self.damage += other.damage
            self.damage |= other.type
        elif isinstance(other, DamageTypes):
            self.type |= other
        self.damage = round(self.damage, 2)
        return self