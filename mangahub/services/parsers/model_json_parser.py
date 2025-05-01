from pydantic import BaseModel
from services.handlers import JsonHandler


class ModelJsonParser[ModelType: BaseModel]:
    def __init__(self, file, model: ModelType):
        self.model = model
        self.json_parser = JsonHandler(file)

    def get(self) -> ModelType:
        return self.model.model_validate(self.json_parser.get())

    def save(self, model: ModelType) -> None:
        self.json_parser.save(model.model_dump())
