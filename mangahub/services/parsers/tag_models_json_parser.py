from pathlib import Path
from .models_json_parser import ModelsJsonParser
from models.tags import TagModel


class TagModelsJsonParser[KeyType: (str | int | float), ModelType: TagModel](ModelsJsonParser[KeyType, ModelType]):
    def __init__(self, file: Path | str, model: ModelType, key_type: KeyType):
        super().__init__(file, model, key_type)
        
    def save(self, data=None):
        data = data if data is not None else self._models_collection
        models_changed = False
        for model in data.values():
            if model._changed:
                models_changed = True
                break

        if models_changed:
            super().save()