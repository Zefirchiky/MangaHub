from pydantic import BaseModel


class SiteTitlePage(BaseModel):
    url_format: str = ''
    
    name_class: str = ''
    name_alt: str = ''
    name_id: str = ''
    
    cover_class: str = ''
    cover_alt: str = ''
    cover_id: str = ''