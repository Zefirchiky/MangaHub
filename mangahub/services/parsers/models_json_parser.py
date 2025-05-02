from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel
from loguru import logger
from services.handlers import JsonHandler


class ModelsJsonParser[KeyType: (str | int | float), ModelType: BaseModel]:
    def __init__(self, file: Path | str, model: ModelType, key_type: KeyType):
        self.file = file
        self.model = model
        self.key_type = key_type
        self.json_parser = JsonHandler(self.file)
        self._models_collection: dict[KeyType, ModelType] = {}

    def add(self, name: KeyType, model: ModelType):
        self._models_collection[name] = model
    
    def get(self, name: KeyType) -> ModelType | None:
        if name in self._models_collection.keys():
            return self._models_collection[name]

        try:
            if data := self.json_parser.get().get(str(name)):
                model = self.model.model_validate(data)
                self._models_collection[name] = model
                return model
            logger.warning(
                f"Model not found: {self.model}({name})\nfile: {self.file}\nkey type: {self.key_type}\nname type: {type(name)}"
            )
            return None
        except KeyError:
            logger.error(f"{model.__name__} {name} not found")
            return
        
    def pop(self, name: KeyType):
        return self._models_collection.pop(name)

    def get_all(self) -> dict[KeyType, ModelType]:
        for name in self.json_parser.get().keys():
            name = self.key_type(name)
            self.get(name)

        return self._models_collection

    @property
    def models_collection(self) -> dict[KeyType, ModelType]:
        if self._models_collection:
            return self._models_collection
        return self.get_all()

    @models_collection.setter
    def models_collection(self, models_dict: dict[KeyType, ModelType]):
        self._models_collection = models_dict

    def save(self, data: dict[KeyType, ModelType]=None):
        data = data if data is not None else self._models_collection
        models_list = {
            name: model.model_dump(mode="json") for name, model in data.items()
        }
        self.json_parser.save(models_list)
