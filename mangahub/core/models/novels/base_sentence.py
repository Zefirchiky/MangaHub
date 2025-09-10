from core.models.tags.tag_model import TagModel
from .base_word import BaseWord
from .novel_word import Word, Punctuation

PUNCTUATIONS = ['.', '!', '?', ',', ':', '-']
EOF_CHARS = ['.', '!', '?']


class BaseSentence(TagModel):
    words: list[BaseWord] = []
    
    def add_chars(self, chars: str):
        for char in chars:
            self.add_char(char)
        return self
    
    def add_char(self, char: str):
        if not self.words:
            if char == ' ':
                return self
            if char in PUNCTUATIONS:
                self.words.append(Punctuation(text=char))
            else:
                self.words.append(Word(text=char))
                
        else:
            last_word = self.words[-1]
            if char == ' ':
                if not last_word.text:
                    return self
                if isinstance(last_word, Word):
                    last_word.check()
                self.words.append(Word())
                return self
            
            if char in PUNCTUATIONS:
                if isinstance(last_word, Word):
                    last_word.check()
                if isinstance(last_word, Punctuation):
                    last_word.text += char
                elif last_word.text:
                    self.words.append(Punctuation(text=char))
                else:
                    self.words[-1] = Punctuation(text=char)
            
            else:
                last_word.text += char
        return self
    
    def is_last_char_eof(self):
        if not self.words:
            return False
        if isinstance(self.words[-1], Punctuation):
            if self.words[-1].text[-1] in EOF_CHARS:
                return True
        return False
    
    @classmethod
    def from_chars(cls, chars):
        sentence = cls()
        return sentence.add_chars(chars)

    @property
    def text(self) -> str:
        t = ""
        for i, word in enumerate(self.words):
            if isinstance(word, Punctuation):
                t += str(word)
                continue
            
            if i != 0:
                t += ' '
            t += str(word)
        return t
    
    @property
    def content(self) -> str:
        ' '.join([str(word) for word in self.words])
    
    def __str__(self) -> str:
        return self.text
    
    def __len__(self) -> int:
        return len(self.text)