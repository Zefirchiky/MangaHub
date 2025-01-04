from enum import Flag


class DamageTypes(Flag):
    NORMAL      = 0b001     # Normal damage
    TRUE        = 0b010     # Ignores defense
    PERCENTAGE  = 0b100     # Takes a percentage of the target's health as default
    
    
class CustomDamageType:
    def __init__(self, value: int=0):
        self.value = value
        
    def add_damage_type(self, value: int=0, type: DamageTypes=DamageTypes.NORMAL) -> 'CustomDamageType':
        return self
    
    def add_continuous_damage(self, damage_per_ms: int=0, time_ms: int=0, type: DamageTypes=DamageTypes.NORMAL) -> 'CustomDamageType':
        return self