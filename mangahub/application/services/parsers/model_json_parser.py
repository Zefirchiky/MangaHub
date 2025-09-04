import typing
from pydantic import BaseModel
from application.services.handlers import JsonHandler


MT = typing.TypeVar('MT', bound=BaseModel)

class ModelJsonParser(typing.Generic[MT]):
    def __init__(self, file, model: MT):
        self.model = model
        self.json_parser = JsonHandler(file)

    def get(self) -> MT:
        return self.model.model_validate(self.json_parser.get())

    def save(self, model: MT) -> None:
        self.json_parser.save(model.model_dump())
