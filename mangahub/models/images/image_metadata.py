from pydantic import BaseModel


class ImageMetadata(BaseModel):
    url: str
    name: str = ''
    width: int = 0
    height: int = 0
    size: int = 0
    format: str = ''
    size: int = 0
    cached_path: str = ''