import re
from pydantic import BaseModel, field_validator


class SiteChapterPage(BaseModel):
    url_format: str
    
    title_class: str = ''
    title_alt: str = ''
    title_id: str = ''