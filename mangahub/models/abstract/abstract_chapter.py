from abc import ABC
from ..tags.tag_model import TagModel


class AbstractChapter(ABC, TagModel):
    number: int | float
    name: str = ''
    upload_date: str = ''
    translator: str = ''
    language: str = 'en'