from pydantic import BaseModel


class ImageParsingMethod(BaseModel):
    is_set: bool = False
    
    read_from_script: bool = False
    url_regex: str = None
    
    read_from_html: bool = False
    class_: str | None = None
    id_format: str | None = None
    alts_format: str | None = None
    
    def set_url_regex(self, url_regex: str) -> None:
        self.reset()
        self.is_set = True
        self.read_from_script = True
        self.url_regex = url_regex
        return self
        
    def set_read_from_html(self, images_html_class: str = None, images_id_format: str = None, images_html_alts_format: str = None) -> None:
        self.reset()
        self.is_set = True
        self.read_from_html = True
        self.class_ = images_html_class
        self.id_format = images_id_format
        self.alts_format = images_html_alts_format
        return self
        
    def reset(self) -> None:
        self.__init__()