from loguru import logger
from pydantic import BaseModel
from services.handlers import JsonHandler
from utils import MM


class ModelsJsonParser:
    def __init__(self, file, model: BaseModel):
        self.file = file
        self.model = model
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self._models_collection: dict[str | float, BaseModel] = {}
        
    def get_model(self, name: str | int | float) -> BaseModel:
        if name in self._models_collection.keys():
            return self._models_collection[name]
        
        try:
            data = self.data.get(str(name))
            if data:
                model = self.model.model_validate(data)
                self._models_collection[name] = model
                return model
            raise Exception(f'Model not found: {name}')
        except KeyError:
            logger.warning(f"{model.__name__} {name} not found")
            MM.show_message('error', f"{model.__name__} {name} not found")
            return 
        
    def get_all_models(self) -> dict[str | float, BaseModel]:
        for name in self.data.keys():
            if name not in self._models_collection.keys():
                self._models_collection[name] = self.get_model(name)
        
        return self._models_collection
    
    @property
    def models_collection(self) -> dict[str | float, BaseModel]:
        if self._models_collection:
            return self._models_collection
        return self.get_all_models()
    
    @models_collection.setter
    def models_collection(self, models_dict: dict[str | float, BaseModel]):
        self._models_collection = models_dict
    
    def save(self, models_dict: dict[str, BaseModel]):
        models_list = {name: model.model_dump(mode="json", exclude_unset=True, exclude_none=True) for name, model in models_dict.items()}
        self.json_parser.save_data(models_list)