from __future__ import annotations

from models.tags.tag_model import TagModel
from pydantic import field_validator


class TextElement(TagModel):
    text: str
    
    @field_validator('text')
    def validate_text(cls, text: str) -> str:
        return text.strip().replace('\n', '')
    
    
    def __str__(self) -> str:
        return self.text
    
    def __add__(self, text: TextElement | str) -> 'TextElement':
        if isinstance(text, TextElement):
            text = text.text
        self.text += text
        return self