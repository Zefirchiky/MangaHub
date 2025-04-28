from pathlib import Path
from loguru import logger
from pydantic import BaseModel
from services.handlers import JsonHandler
from utils import MM


class ModelsJsonParser[KT: (str | int | float), T: BaseModel]:
    def __init__(self, file: Path | str, model: T, key_type: KT):
        self.file = file
        self.model = model
        self.key_type = key_type
        self.json_parser = JsonHandler(self.file)
        self.data = self.json_parser.get_data()
        self._models_collection: dict[KT, T] = {}
        
    def get(self, name: KT) -> T:
        if name in self._models_collection.keys():
            return self._models_collection[name]
        
        try:
            if data := self.data.get(str(name)):
                model = self.model.model_validate(data)
                self._models_collection[name] = model
                return model
            raise Exception(f'Model not found: {self.model}({name})\n(file: {self.file}\nkey type: {self.key_type} (.get(str(name)))\nname type: {type(name)})')
        except KeyError:
            MM.show_error(f"{model.__name__} {name} not found")
            return 
        
    def get_all(self) -> dict[KT, T]:
        for name in self.data.keys():
            name = self.key_type(name)
            self.get(name)
        
        return self._models_collection
    
    @property
    def models_collection(self) -> dict[KT, T]:
        if self._models_collection:
            return self._models_collection
        return self.get_all()
    
    @models_collection.setter
    def models_collection(self, models_dict: dict[KT, T]):
        self._models_collection = models_dict
    
    def save(self, models_dict: dict[KT, T]):
        models_list = {name: model.model_dump(mode="json") for name, model in models_dict.items()}
        self.json_parser.save_data(models_list)