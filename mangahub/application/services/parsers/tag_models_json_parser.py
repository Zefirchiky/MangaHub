from pathlib import Path
from .models_json_parser import ModelsJsonParser
from core.models.tags import TagModel


class TagModelsJsonParser[KT: (str | int | float), MT: TagModel](ModelsJsonParser[KT, MT]):
    def __init__(self, file: Path | str, model: MT, key_type: KT):
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