from __future__ import annotations

from ..tags.tag_model import TagModel
from .base_sentence import BaseSentence
from .novel_text_elements import Thought, Dialog, Narration
from .base_text_element import BaseTextElement
import time


class NovelParagraph(TagModel):
    elements: list[BaseTextElement] = []

    def insert_chars(self, index: int, chars: str):
        element_types_map: dict[str, BaseTextElement] = {
            "'": Thought,
            '"': Dialog,
        }
        text_el = self.get_element_with_index(index)
        for i, ch in enumerate(chars):
            if ch in element_types_map: # Handles all special case character (', ")
                if text_el: # If not first element
                    if isinstance(text_el, element_types_map[ch]):
                        if not text_el.is_end:
                            text_el.is_end = True
                        else:
                            text_el = element_types_map[ch](start_at=i+index)
                            self.elements.append(text_el)
                    else:
                        if not text_el.is_end:
                            text_el.is_end = True
                        else:
                            text_el = element_types_map[ch](start_at=i+index)
                            self.elements.append(text_el)
                            # text_el.add_char(ch)    # TODO: Handling of 'text "text" text' ('""')
                else:
                    text_el = element_types_map[ch](start_at=i+index)
                    self.elements.append(text_el)

            # Only other characters
            else:
                if ch == ' ' and text_el.is_end:
                    continue
                if text_el is not None and not text_el.is_end:
                    text_el.add_char(ch)
                else:
                    text_el = Narration(start_at=i+index).add_char(ch)
                    self.elements.append(text_el)
        
        return self
    
    def add_chars(self, chars: str):
        element_types_map: dict[str, BaseTextElement] = {
            "'": Thought,
            '"': Dialog,
        }
        text_el = self.elements[-1] if self.elements else None
        index = len(self)
        for i, ch in enumerate(chars):
            t = time.perf_counter()
            if ch in element_types_map:
                if text_el is not None:
                    if isinstance(text_el, element_types_map[ch]):  # If its the same, close
                        text_el.is_end = True
                        if not text_el.sentences[-1].text:
                            del text_el.sentences[-1]
                    elif not isinstance(text_el, Narration):        # If its " inside of Though, just add
                        text_el.add_char(ch)
                    else:                                           # If its Narration, end it and create new TextElement
                        text_el.is_end = True
                        if not text_el.sentences[-1].text:
                            del text_el.sentences[-1]
                        self.elements.append(element_types_map[ch](start_at=i+index))
                
                else:                                               # If self.elements is empty, start with current needed
                    self.elements.append(element_types_map[ch](start_at=i+index))
            
            else:
                if text_el and text_el.is_end and ch == ' ':        # Skip space after end of TextElement
                    continue
                if text_el is not None:
                    if text_el.is_end:                              # If previous element ended and new one is not of special types, add Narration
                        text_el = Narration(start_at=i+index)
                        self.elements.append(text_el)
                        text_el.add_char(ch)
                    else:                                           # Just continue with current element
                        text_el.add_char(ch)
                else:
                    text_el = Narration(start_at=i+index)
                    self.elements.append(text_el)
                    text_el.add_char(ch)
            # print(ch, time.perf_counter() - t)

        print(self.elements)
                
        return self

    def is_sentence_start(self) -> bool:
        text = self.text
        return text[0].isupper() or not text[0].isalnum() or not text[0].isspace()

    def validate_elements(self) -> NovelParagraph:
        i = 0
        while i < len(self.elements) - 1:
            if type(self.elements[i]) is not type(self.elements[i + 1]):
                self.elements[i] += self.elements[i + 1]
                self.elements.pop(i + 1)
            else:
                i += 1
        return self
    
    def get_element_with_index(self, i: int):
        cur_len = 0
        for sentence in self.elements:
            cur_len += len(sentence)
            if i <= cur_len:
                return sentence
        return False
    
    def get_element_with_offset(self, offset: int):
        cur_len = 0
        for sentence in self.elements:
            cur_len += len(sentence)
            

    @property
    def text(self) -> str:
        return " ".join([str(element) for element in self.elements])

    def __str__(self) -> str:
        return self.text
    
    def __len__(self) -> int:
        return sum([len(sentence) for sentence in self.elements])

    def __add__(
        self, element: BaseSentence | list[BaseSentence] | NovelParagraph | str
    ) -> NovelParagraph:
        if isinstance(element, NovelParagraph):
            self.elements.extend(element.elements)
            return self
        if isinstance(element, list):
            self.elements.extend(element)
            return self
        if isinstance(element, str):
            element = BaseSentence(text=element)
        self.elements.append(element)
        return self
