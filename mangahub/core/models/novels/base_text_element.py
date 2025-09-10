from core.models.tags import TagModel
from .base_sentence import BaseSentence

EOF_CHARS = ['.', '!', '?']


class BaseTextElement(TagModel):
    sentences: list[BaseSentence] = []
    start_at: int
    is_end: bool=False
    
    def insert_chars(self, i, chars: str):
        eof_in_chars = False
        
        return self
    
    def add_char(self, char: str):
        if not self.sentences:
            if char == ' ':
                return self
            self.sentences.append(BaseSentence().add_char(char))
        else:
            if char in EOF_CHARS:
                self.sentences[-1].add_char(char) 
            else:
                if self.sentences[-1].is_last_char_eof():
                    self.sentences.append(BaseSentence())
                self.sentences[-1].add_char(char)
        return self
    
    def get_sentence_with_index(self, i: int):
        cur_len = 0
        for sentence in self.sentences:
            cur_len += len(sentence)
            if i <= cur_len:
                return sentence
    
    def set_is_start(self, value: bool=True):
        self.is_start = value
        return self
    
    def set_is_end(self, value: bool=True):
        self.is_end = value
        return self
    
    @classmethod
    def from_chars(cls, chars):
        return cls().insert_chars(0, chars)
    
    @property
    def text(self):
        return ' '.join([str(sentence) for sentence in self.sentences])
    
    @property
    def content(self):
        return ' '.join([str(sentence) for sentence in self.sentences])
    
    def __str__(self) -> str:
        return self.text
    
    def __len__(self) -> int:
        return len(self.text)