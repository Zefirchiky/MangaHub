


class System:
    def __init__(self, name: str='') -> None:
        # === Class Variables ===
        self.name = name
        
        # === System ===
        self._power: int = 0
    
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