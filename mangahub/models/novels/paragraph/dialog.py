from models.abstract import TextElement


class Dialog(TextElement):
    speaker: str = ""
    target: str = ""

    @property
    def content(self) -> str:
        return self.text[1:-2]
