from pydantic import BaseModel, PrivateAttr
from typing import Self


class TagModel(BaseModel):
    tags: set[str] = set()
    _changed = PrivateAttr(False)

    def add_tag(self, tag_name: str) -> Self:
        self._changed = True
        self.tags.add(tag_name)
        return self

    def remove_tag(self, tag_name: str) -> Self:
        self._changed = True
        self.tags.remove(tag_name)
        return self
        
    def set_changed(self, value: bool=True) -> Self:
        self._changed = value
        return self

    def __add__(self, tag_name: str) -> "TagModel":
        self._changed = True
        return TagModel(tags=self.tags | {tag_name})
