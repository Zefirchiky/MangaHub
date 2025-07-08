from __future__ import annotations

from ..tags.tag_model import TagModel
from .base_sentence import BaseSentence
from .novel_sentence import Thought, Dialog, Narration
from .novel_word import Word, Punctuation


class NovelParagraph(TagModel):
    sentences: list[BaseSentence, str] = []

    def add_chars(self, i: int, chars: str):
        print(len(self), i)
        if len(self) <= i:
            print(chars)
            for char in chars:
                print(repr(chars))
                if not self.sentences:
                    if char == ' ':
                        continue
                    
                    if char == "'":
                        self.sentences.append(Thought())
                    elif char == '"':
                        self.sentences.append(Dialog())
                    else:
                        sentence = Narration()
                        sentence.words.append(Word(text=char))
                        self.sentences.append(sentence)

                if not (w := self.sentences[-1].words):
                    w.append(Word())

                if char == ' ':
                    # if space:
                    #   if prev sentence is space - skip (No 2 spaces in a row)
                    #   if prev word is space - skip (No 2 spaces in a row)
                    #   else - add 
                    if self.sentences[-1] == ' ':
                        continue 
                    
                    sentence = self.sentences[-1]
                    if sentence.words[-1] == ' ':
                        continue
                    
                    word = sentence.words[-1]
                    if isinstance(word, Punctuation) and word.text[-1] in '.!?':
                        self.sentences.append(' ')

                    else:
                        self.sentences[-1].words.append(' ')
                
                elif char in ',.!?':
                    if not isinstance(self.sentences[-1].words[-1], Punctuation):
                        self.sentences[-1].words.append(Punctuation())

                    elif isinstance(self.sentences[-1].words[-1], Punctuation):
                        self.sentences[-1].words[-1].text += char

                elif char == '"':
                    if isinstance(self.sentences[-1], Dialog):
                        continue
                    self.sentences.append(Dialog())

                else:
                    if self.sentences[-1] == ' ':
                        sentence = Narration()
                        sentence.words.append(Word(text=char))
                        self.sentences.append(sentence)
                        continue
                    if not self.sentences[-1].words:
                        self.sentences[-1].words.append(Word())
                    self.sentences[-1].words[-1].text += char
        
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
