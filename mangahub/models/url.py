import re
from pydantic import BaseModel, PrivateAttr, field_validator


class URL(BaseModel):
    url: str
    regex: str = ''
    _cached_elements: list[str] = PrivateAttr(default_factory=list)
    
    def __init__(self, url: str, regex: str=''):
        super().__init__(url=url, regex=regex)
    
    @field_validator('url')
    def validate_url(cls, value) -> str:
        if not URL.is_url(value):
            raise ValueError("Invalid URL")
        return URL.make_url(value)
    
    def with_domain(self, domain: str) -> 'URL':
        return URL(f"{self.protocol}{domain}/{self.path}")
    
    def remove_suffix(self, suffix: str='', number: int=0) -> 'URL':
        if suffix:
            url = self.url.removesuffix(suffix)
        
        if number:
            for _ in range(number):
                url = self.url.removesuffix('/' + self.suffix)
        
        if url != self.url:
            self.url = url

        return self
    
    @staticmethod
    def is_url(url: str) -> bool:
        return re.match(re.compile(
                            r'^(https?:\/\/)?'  # Match the protocol (http or https) (optional)
                            r'((([a-zA-Z\d]([a-zA-Z\d-]*[a-zA-Z\d])*)\.)+[a-zA-Z]{2,}|'  # Match domain
                            r'((\d{1,3}\.){3}\d{1,3}))'  # Match IPv4 address
                            r'(:\d+)?'  # Match optional port
                            r'(\/[-a-zA-Z\d%_.~+]*)*'  # Match path
                            r'(\?[;&a-zA-Z\d%_.~+=-]*)?'  # Match query string
                            r'(#[-a-zA-Z\d_]*)?$'  # Match fragment
                        ), url) is not None
    
    @staticmethod
    def make_url(url: str) -> str:
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
        if 'www.' in url:
            url = url.replace('www.', '')
        return url
        
    @property
    def url(self) -> str:
        return self._url
    
    @url.setter
    def url(self, url: str):
        if not URL.is_url(url):
            raise ValueError("Invalid URL")
        self._url = self.make_url(url)
        self._cached_elements = None
    
    @property
    def IPv4(self) -> str:
        return re.match(r'((\d{1,3}\.){3}\d{1,3})', self.url).group(0)
    
    @property
    def protocol(self) -> str:
        return self.url.split('://')[0] + '://'
    
    @property
    def site(self) -> str:
        return self.elements[1]
    
    @property
    def site_url(self) -> str:
        return self.protocol + self.site
    
    @property
    def root_domain(self) -> str:
        return self.site.split('.')[0]
    
    @property
    def top_domain(self) -> str:
        return '.' + self.site.split('.')[1]

    @property
    def full_site(self) -> str:
        return self.protocol + self.site
    
    @property
    def stem(self) -> str:
        return self.protocol + '/'.join(self.elements[1:-1])
    
    @property
    def subdirectory(self) -> str:
        return self.elements[2]
    
    @property
    def path(self) -> str:
        return '/'.join(self.elements[2:])
    
    @property
    def suffix(self) -> str:
        return self.elements[-1]
    
    @property
    def elements(self) -> list:
        if not self._cached_elements:
            self._cached_elements = [x for x in self.url.split('/') if x and x != 'www.']
        return self._cached_elements
    
    def __eq__(self, other):
        return self.url == other
    
    def __add__(self, key: str) -> 'URL':
        return URL(f"{self.url}/{key}")
    
    def __truediv__(self, key: str) -> 'URL':
        return URL(f"{self.url}/{key}")
    
    def __str__(self) -> str:
        return self.url
    
    def __repr__(self) -> str:
        return self.url
    
    def __hash__(self):
        return hash(self.url)
    