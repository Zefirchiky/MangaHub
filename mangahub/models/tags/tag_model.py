from pydantic import BaseModel


class TagModel(BaseModel):
    tags: set[str] = set()

    def add_tag(self, tag_name: str) -> None:
        self.tags.add(tag_name)

    def remove_tag(self, tag_name: str) -> None:
        self.tags.remove(tag_name)

    def __add__(self, tag_name: str) -> "TagModel":
        return TagModel(tags=self.tags | {tag_name})
