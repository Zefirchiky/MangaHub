from pydantic import BaseModel
from services.handlers import JsonHandler


class ModelJsonParser:
    def __init__(self, file, model: BaseModel):
        self.file = file
        self.model = model
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        
    def get_model(self) -> BaseModel:
        return self.model.model_validate(self.data)
    
    def save(self, model: BaseModel) -> None:
        self.json_parser.save_data(model)