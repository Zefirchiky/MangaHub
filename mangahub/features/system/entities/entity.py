from system.models.damage import Damage
from system.models.attack import Attack
from system.models.skill import Skill
from system.models.defense import Defense
from system.utils.enums import EntityStatus


class Entity:
    Status = EntityStatus
    
    base_hp = 100
    base_def = None
    
    def __init__(
            self, name: str='auto', 
            hp: int=0, defense: Defense=None,
            status: EntityStatus=EntityStatus.ALIVE
        ) -> None:
        if name == 'auto':
            name = f'Entity_{id(self)}'
        self._name = name
        
        # === Entity ===
        if hp == 0:
            hp = self.base_hp
        self.max_hp: int = hp
        self.hp: float = hp
        
        if not defense:
            defense = [self.base_def] if self.base_def else []
        self.defense = defense if defense else []
        
        self.power: int = 0
        self.status = status
        
        self.skills = {}
        
        self.is_unknown = False
    
    def attack(self, target: 'Entity', attack: Attack) -> 'Entity':
        attack.attacker = self
        attack.target = target
        attack.attack()
        return self
    
    def damaged(self, damage: float) -> 'Entity':
        self.hp -= damage
        self.hp = max(0, self.hp)
        self.hp = round(self.hp, 2)
        if self.hp <= 0:
            self.status = EntityStatus.DEAD
        return self
            
    def unknown(self, is_unknown: bool=True) -> 'Entity':
        self.is_unknown = is_unknown
        return self
    
    def add_skill(self, skill: Skill) -> 'Entity':
        self.skills[skill.name] = skill
        return self
    
    def add_defense(self, defense: Defense) -> 'Entity':
        self.defense.append(defense)
        return self
    
    @property
    def name(self) -> str:
        return 'Unknown' if self.is_unknown else self._name
    
    def __repr__(self) -> str:
        return f'{self.name} ({self.hp}/{self.max_hp} HP) ({self.defense} DEF)    Status: {self.status.name}'
        