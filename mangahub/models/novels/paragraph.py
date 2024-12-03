from ..tags.tag_model import TagModel


class Paragraph(TagModel):
    text: str
    
    @property
    def sentences(self) -> list[str]:
        return self.text.split('.')