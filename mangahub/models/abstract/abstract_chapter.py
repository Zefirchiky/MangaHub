from abc import ABC

from ..tags.tag_model import TagModel


class AbstractChapter(ABC, TagModel):
    number: int | float
    name: str = ''
    upload_date: str = ''
    translator: str = ''
    language: str = 'en'
    
    is_read: bool = False
    
    def set_is_read(self, is_read: bool=True):
        self.is_read = is_read