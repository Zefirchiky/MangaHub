from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel
from loguru import logger
from services.handlers import JsonHandler


class ModelsJsonParser[KT, MT: BaseModel]:
    def __init__(self, file: Path | str, model: MT, key_type: KT):
        self.file = file
        self.model = model
        self.key_type = key_type
        self.json_parser = JsonHandler(self.file)
        self._models_collection: dict[KT, MT] = {}

    def add(self, name: KT, model: MT):
        self._models_collection[name] = model
    
    def get(self, name: KT, default=None) -> MT | None:
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
            return default
        except KeyError:
            logger.error(f"{model.__name__} {name} not found")
            return
        
    def get_i(self, index: int, default=None) -> MT:
        if not self.json_parser.data:
            self._models_collection.update(self.json_parser.get())
        col_len = len(self)
        if index < 0:
            index = col_len + index
        if index < 0 or index >= col_len:
            if default == 'err':
                raise IndexError(f'Index is out of range. Index: {index}, max: {col_len}')
            return default
        return self.get((list(self.json_parser.data.keys()) + list(self._models_collection.keys()))[index])
        
    def pop(self, name: KT):
        return self._models_collection.pop(name)

    def get_all(self) -> dict[KT, MT]:
        for name in self.json_parser.get().keys():
            name = self.key_type(name)
            self.get(name)

        return self._models_collection

    @property
    def models_collection(self) -> dict[KT, MT]:
        if self._models_collection:
            return self._models_collection
        return self.get_all()

    @models_collection.setter
    def models_collection(self, models_dict: dict[KT, MT]):
        self._models_collection = models_dict

    def __len__(self) -> int:
        return len(self.json_parser) + len(self._models_collection)
    
    def __str__(self) -> str:
        return f'ModelsJsonParser: first ell: {self.get_i(0, None)}, _models_collection length: {len(self.json_parser)}'

    def save(self, data: dict[KT, MT]=None):
        data = data if data is not None else self._models_collection
        models_list = {
            name: model.model_dump(mode="json") for name, model in data.items()
        }
        self.json_parser.save(models_list)
