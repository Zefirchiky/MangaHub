from .base_sentence import BaseSentence


class Dialog(BaseSentence):
    by: str = ""
    to: str = ""

    @property
    def text(self) -> str:
        return f'"{self.content}"'


class Narration(BaseSentence):
    pass


class Thought(BaseSentence):
    by: str = ''
    
    @property
    def text(self) -> str:
        return f"'{self.content}'"