from typing import Union

from pydantic import field_validator
from models.tags.tag_model import TagModel


class TextElement(TagModel):
    text: str
    
    @field_validator('text')
    def validate_text(cls, text: str) -> str:
        if text[0] == ' ':
            text = text[1:]
        if text[-1] == ' ':
            text = text[:-1]
        return text.replace('\n', '')
    
    
    def __str__(self) -> str:
        return self.text
    
    def __add__(self, text: Union['TextElement', str]) -> 'TextElement':
        if isinstance(text, TextElement):
            text = text.text
        self.text += text
        return self