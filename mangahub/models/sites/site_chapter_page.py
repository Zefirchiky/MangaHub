from pydantic import BaseModel


class SiteChapterPage(BaseModel):
    url_format: str
    
    title_class: str = ''
    title_alt: str = ''
    title_id: str = ''