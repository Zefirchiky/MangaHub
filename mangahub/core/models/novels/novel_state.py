from pydantic import BaseModel
from core.models.novels import Novel


class NovelState(BaseModel):
    novel: Novel | None = None
    chapter_num: int | None = None