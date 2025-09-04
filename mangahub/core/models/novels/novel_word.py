from typing import Self, ClassVar
from .base_word import BaseWord
from enchant import Dict


class Punctuation(BaseWord):
    pass

class Word(BaseWord):
    is_misspelled: bool = False
    suggestions: list[str] = []
    _en_dict: ClassVar[Dict] = Dict('en_US')
    
    def check(self) -> bool:
        if not self._en_dict.check(self.text):
            self.is_misspelled = True
            self.suggestions.extend(self._en_dict.suggest(self.text))
            return False
        return True
    
class DefinedWord(Word):
    definition: str = ''
    
    def define(self, definition: str) -> Self:
        self.is_misspelled = False
        self.definition = definition
        return self