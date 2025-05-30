from pydantic import BaseModel
from services.handlers import JsonHandler


class ModelJsonParser[MT: BaseModel]:
    def __init__(self, file, model: MT):
        self.model = model
        self.json_parser = JsonHandler(file)

    def get(self) -> MT:
        return self.model.model_validate(self.json_parser.get())

    def save(self, model: MT) -> None:
        self.json_parser.save(model.model_dump())
