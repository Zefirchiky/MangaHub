from pathlib import Path
from pydantic import BaseModel
from services.handlers import JsonHandler
from utils import MM


class ModelsJsonParser[KeyType: (str | int | float), ModelType: BaseModel]:
    def __init__(self, file: Path | str, model: ModelType, key_type: KeyType):
        self.file = file
        self.model = model
        self.key_type = key_type
        self.json_parser = JsonHandler(self.file)
        self._models_collection: dict[KeyType, ModelType] = {}

    def get(self, name: KeyType) -> ModelType:
        if name in self._models_collection.keys():
            return self._models_collection[name]

        try:
            if data := self.json_parser.get().get(str(name)):
                model = self.model.model_validate(data)
                self._models_collection[name] = model
                return model
            raise Exception(
                f"Model not found: {self.model}({name})\n(file: {self.file}\nkey type: {self.key_type} (.get(str(name)))\nname type: {type(name)})"
            )
        except KeyError:
            MM.show_error(f"{model.__name__} {name} not found")
            return

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

    def save(self, models_dict: dict[KeyType, ModelType]):
        models_list = {
            name: model.model_dump(mode="json") for name, model in models_dict.items()
        }
        self.json_parser.save(models_list)
