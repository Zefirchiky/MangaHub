from .models.skill import Skill


class System:    
    def __init__(self, name: str='', is_hidden=False) -> None:
        # === Class Variables ===
        self.name = name
        
        
        # === System ===
        self._power: int = 0
        
        self._attributes = {}
        self.skills = {}
        
    def add_attribute(self, name: str, value: int) -> 'System':
        self._attributes[name] = value
        return self
        
    def add_skill(self, skill: Skill) -> 'System':
        self.skills[skill.name] = skill
        return self
    
    def print(self) -> str:
        system_str = self.str
        print(system_str)
        return system_str
        
    @property
    def power(self) -> int:
        return self._power
    
    @property
    def str(self) -> str:
        return f'''
        === {self.name} ===
        Power: {self.power}
        '''