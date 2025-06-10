from __future__ import annotations

from ..tags.tag_model import TagModel
from .base_sentence import BaseSentence
from .novel_sentence import Thought, Dialog, Narration
from .novel_word import Word, Punctuation


class NovelParagraph(TagModel):
    sentences: list[BaseSentence, str] = []

    def add_chars(self, i: int, chars: str):
        if len(self) - 1 < i:
            for char in chars:
                if char == ' ':
                    if not self.sentences or self.sentences and self.sentences[-1] == ' ':
                        continue 
                    
                    sentence = self.sentences[-1]
                    if not sentence.words or sentence.words and sentence.words[-1] == ' ':
                        continue
                

        
        return self

    def is_sentence_start(self) -> bool:
        text = self.text
        return text[0].isupper() or not text[0].isalnum() or not text[0].isspace()

    def validate_elements(self) -> NovelParagraph:
        i = 0
        while i < len(self.sentences) - 1:
            if type(self.sentences[i]) is not type(self.sentences[i + 1]):
                self.sentences[i] += self.sentences[i + 1]
                self.sentences.pop(i + 1)
            else:
                i += 1
        return self
    
    def get_element_with_offset(self, offset: int):
        cur_len = 0
        for sentence in self.sentences:
            cur_len += len(sentence)
            

    @property
    def text(self) -> str:
        return " ".join([str(element) for element in self.sentences])

    def __str__(self) -> str:
        return self.text
    
    def __len__(self) -> int:
        return sum([len(sentence) for sentence in self.sentences])

    def __add__(
        self, element: BaseSentence | list[BaseSentence] | NovelParagraph | str
    ) -> "NovelParagraph":
        if isinstance(element, NovelParagraph):
            self.sentences.extend(element.sentences)
            return self
        if isinstance(element, list):
            self.sentences.extend(element)
            return self
        if isinstance(element, str):
            element = BaseSentence(text=element)
        self.sentences.append(element)
        return self
