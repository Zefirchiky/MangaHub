from enum import Flag


class DefenseTypes(Flag):
    NORMAL      = 0b001     # Normal defense
    TRUE        = 0b010     # Blocks any damage *(including true if defense_over_damage is True)
    PERCENTAGE  = 0b100     # Takes a percentage of the target's health as default
    
    
class CustomDefenseType:
    def __init__(self, value: int=0):
        self.value = value
        
    def add_defense_type(self, value: int=0, type: DefenseTypes=DefenseTypes.NORMAL) -> 'CustomDefenseType':
        return self