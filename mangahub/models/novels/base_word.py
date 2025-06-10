from pydantic import BaseModel


class BaseWord(BaseModel):
    text: str

    def __len__(self) -> int:
        return len(self.text)
    
    def __str__(self) -> int:
        return self.text