from pydantic import BaseModel


class ImageParsingMethod(BaseModel):
    is_set: bool = False
    
    regex_from_html: bool = False
    url_regex: str | None = None
    
    bs_from_loaded_html: bool = False
    class_: str | None = None
    id_format: str | None = None
    alts_format: str | None = None
    
    def set_regex_from_html(self, url_regex: str) -> None:
        self.reset()
        self.is_set = True
        self.regex_from_html = True
        self.url_regex = url_regex
        return self
        
    def set_bs_from_loaded_html(self, images_html_class: str = None, images_id_format: str = None, images_html_alts_format: str = None) -> None:
        self.reset()
        self.is_set = True
        self.bs_from_loaded_html = True
        self.class_ = images_html_class
        self.id_format = images_id_format
        self.alts_format = images_html_alts_format
        return self
        
    def reset(self) -> None:
        self.__init__()