from .base_text_element import BaseTextElement


class Dialog(BaseTextElement):
    by: str = ""
    to: str = ""

    @property
    def text(self) -> str:
        return f'"{self.content}"'


class Narration(BaseTextElement):
    pass


class Thought(BaseTextElement):
    by: str = ''
    
    @property
    def text(self) -> str:
        return f"'{self.content}'"
    
class SystemMessage(BaseTextElement):
    ...