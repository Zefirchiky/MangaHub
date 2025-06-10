from models.tags.tag_model import TagModel
from .base_word import BaseWord
from .novel_word import Word 


class BaseSentence(TagModel):
    words: list[BaseWord, str] = []
    
    def add_char(self, char: str):
        if char == ' ':
            if self.words and isinstance(self.words[-1], Word):
                self.words[-1].check()
            self.words.append(Word(text=''))
            return self
        elif not self.words:
            self.words.append(Word(text=char))
            return self
        self.words[-1].text += char
        return self

    @property
    def text(self) -> str:
        return ''.join([str(word) for word in self.words])
    
    @property
    def content(self) -> str:
        ''.join([str(word) for word in self.words])
    
    def __str__(self) -> str:
        return self.text
    
    def __len__(self) -> int:
        return len(self.text)