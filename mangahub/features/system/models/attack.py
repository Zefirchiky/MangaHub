from typing import TYPE_CHECKING

from system.models.skill import Skill
from system.models.weapon import Weapon
from system.models.damage import Damage

if TYPE_CHECKING:
    from system.entities import Entity


class Attack:
    def __init__(
            self, 
            skill: Skill=None, weapon: Weapon=None,
            attacker: 'Entity'=None, target: 'Entity'=None
        ):
        self.skill = skill
        self.weapon = weapon
        self.attacker = attacker
        self.target = target
        
        self._damage_list: list[Damage] = []
        
    def attack(self, attacker: 'Entity'=None, target: 'Entity'=None) -> None:
        if attacker:
            self.attacker = attacker
        if target:
            self.target = target
        self.damage_dealt = self.skill.attack(self.target)
        self.target.damaged(self.get_damage())
        print(self)
        
    @property
    def damage_list(self) -> list[Damage]:
        self._damage_list = []
        for dmg in self.skill.damage:
            self._damage_list.append(dmg)
        return self._damage_list
        
    def get_damage(self) -> float:
        damage_dealt = 0
        for dmg in self.damage_list:
            damage_dealt += self.target.defense(dmg.get_damage(self.target.max_hp, self.target.defense))
        return sum([dmg.get_damage(self.target.max_hp, self.target.defense) for dmg in self.damage_list])
    
    def __repr__(self) -> str:
        string = f'{self.attacker.name} attacked {self.target.name} with [{self.skill.name}]: {self.target.hp}/{self.target.max_hp} (-{self.get_damage()})\n'
        
        for dmg in self.damage_list:
            string += f'\t -{dmg.get_damage(self.target.max_hp, self.target.defense)} by [{dmg.damage} {dmg.type.name} damage]\n'
        
        return string