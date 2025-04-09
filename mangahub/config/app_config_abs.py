import json


class Config:
    """Base config class. Will automatically save all fields of a class and its children"""
    @classmethod
    def get_fields(cls) -> dict[str, ]:
        result = {}
        for name, value in cls.__dict__.items():
            if not name.startswith('_'):
                if isinstance(value, type) and issubclass(value, Config):
                    print(value)
                    result[name] = value.get_fields()
                else:
                    result[name] = value
        return result
    
    @classmethod
    def save(cls, filename: str = 'config.json'):
        with open(filename, 'w') as f:
            json.dump(cls.get_fields(), f, indent=4)
            
    @classmethod
    def load(cls, filename: str = 'config.json'):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            cls._update_from_dict(cls, data)
        except FileNotFoundError:
            print(f"Config file {filename} not found, using defaults")
    
    @classmethod
    def _update_from_dict(cls, target_cls, data: dict[str, ]):
        for key, value in data.items():
            if key in target_cls.__dict__:
                if isinstance(value, dict) and isinstance(target_cls.__dict__[key], type) and issubclass(target_cls.__dict__[key], Config):
                    cls._update_from_dict(target_cls.__dict__[key], value)
                else:
                    setattr(target_cls, key, value)
                    
                    
class Setting:
    def __init__(self, name: str, value):
        self.name = name
        self.value = value
        
    def __call__(self):
        return self