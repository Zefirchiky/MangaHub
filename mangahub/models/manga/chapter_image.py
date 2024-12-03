from ..tags.tag_model import TagModel


class ChapterImage(TagModel):
    number: int
    width: int
    height: int
    image: str = ''