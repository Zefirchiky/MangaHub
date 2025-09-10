from typing import Self, ClassVar
from .base_word import BaseWord
from enchant import Dict
import enchant
import time


class Punctuation(BaseWord):
    pass

class Word(BaseWord):
    is_misspelled: bool = False
    suggestions: list[str] = []
    _en_dict: ClassVar[Dict] = Dict('en_US')
    
    def check(self) -> bool:
        t = time.perf_counter()
        if not self._en_dict.check(self.text):
            print(f'Check for a word {self}: {time.perf_counter()-t}')
            t = time.perf_counter()
            self.is_misspelled = True
            self.suggestions = self._en_dict.suggest(self.text)
            print(f'Suggestions for a word {self}: {time.perf_counter()-t}')
            return False
        
        self.is_misspelled = False
        self.suggestions = []
        return True
    
class DefinedWord(Word):
    definition: str = ''
    
    def define(self, definition: str) -> Self:
        self.is_misspelled = False
        self.definition = definition
        return self