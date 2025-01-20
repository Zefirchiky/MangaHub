from typing import Union

from ..tags.tag_model import TagModel
from models.abstract import TextElement


class NovelParagraph(TagModel):
    elements: list[TextElement] = []
    
    def is_sentence_start(self) -> bool:
        text = self.text
        return text[0].isupper() or not text[0].isalnum() or not text[0].isspace()
    
    def validate_elements(self) -> 'NovelParagraph':
        i = 0
        while i < len(self.elements) - 1:
            if type(self.elements[i]) == type(self.elements[i + 1]):
                self.elements[i] += self.elements[i + 1]
                self.elements.pop(i + 1)
            else:
                i += 1
        return self
    
    
    @property
    def text(self) -> str:
        return ' '.join([str(element) for element in self.elements])
    
    
    def __str__(self) -> str:
        return self.text
    
    def __add__(self, element: Union[TextElement, list[TextElement], 'NovelParagraph', str]) -> 'NovelParagraph':
        if isinstance(element, NovelParagraph):
            self.elements.extend(element.elements)
            return self
        if isinstance(element, list):
            self.elements.extend(element)
            return self
        if isinstance(element, str):
            element = TextElement(text=element)
        self.elements.append(element)
        return self