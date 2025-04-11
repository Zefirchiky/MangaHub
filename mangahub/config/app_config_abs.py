from __future__ import annotations
import json
from pathlib import Path
from typing import Type, get_type_hints, get_origin, get_args, cast
                    
                    
class Setting[T]:
    def __init__(self, value: T, name: str='', options=None, level=1, description=''):
        self._value = value
        self.name = name
        self.options = options
        self.description = description
        
        self._type: Type[T] | None = None
        
    def __set_name__(self, owner: Type, name: str):
        """Called when the Setting is declared in a class."""
        self._attribute_name = name
        
        if hasattr(self, "__orig_class__"):
            origin = get_origin(self.__orig_class__)
            args = get_args(self.__orig_class__)
        elif name in (hints := get_type_hints(owner)):
            origin = get_origin(hints[name])
            args = get_args(origin)
        else:
            raise TypeError('Type must be set, either in type hint, or in generic type')
            
        # Handle cases like Setting[int]
        if origin is Setting and args:
            self._type = args[0]
        
    def __call__(self) -> T:
        return self._value
    
    def __set__(self, instance, value: T) -> None:
        """Set a new value with type checking."""
        if self._type is not None and value is not None and not isinstance(value, self._type):
            try:
                # Try to convert value to the expected type
                value = cast(T, self._type(value))
            except (ValueError, TypeError):
                raise TypeError(f"Value for {self.name} must be of type {self._type.__name__}, got {type(value).__name__}")
        
        self._value = value
        
    def __str__(self) -> str:
        return f'{self.name}: {self._type.__name__}({self()})'
        
    def to_dict(self) -> dict[str, ]:
        """Convert setting to dictionary."""
        try:
            value = self._value.to_dict()
        except Exception:
            print(f'{value} no to_dict')
            value = self._value
        return {
            "value": value,
            "name": self.name,
            "description": self.description
        }
        

class ConfigMeta(type):
    """Metaclass for Config to enable proper inheritance and access patterns."""
    
    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Type:
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Process nested Config classes to make them proper attributes
        for key, value in list(cls.__dict__.items()):
            if isinstance(value, type) and issubclass(value, Config) and value is not Config:
                # Replace the class reference with an instance
                setattr(cls, key, value())
        
        return cls

class Config(metaclass=ConfigMeta):
    """Base configuration class."""
    
    def to_dict(self) -> dict[str, ]:
        """Convert config to dictionary recursively."""
        result = {}
        
        # Process all attributes including inherited ones
        for key, value in vars(self.__class__).items():
            if key.startswith('_'):
                continue
                
            if isinstance(value, Setting):
                print(value)
                result[key] = value()
            elif isinstance(value, Config):
                result[key] = value.to_dict()
                
        return result
    
    def to_dict_with_metadata(self) -> dict[str, ]:
        """Convert config to dictionary with full setting metadata."""
        result = {}
        
        for key, value in vars(self.__class__).items():
            if key.startswith('_'):
                continue
                
            if isinstance(value, Setting):
                result[key] = value.to_dict()
            elif isinstance(value, Config):
                result[key] = value.to_dict_with_metadata()
                
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, ]) -> Config:
        """Create config instance from dictionary."""
        instance = cls()
        
        for key, value in data.items():
            attr = getattr(instance.__class__, key, None)
            
            if isinstance(attr, Setting):
                setattr(instance.__class__, key, value)
            elif isinstance(attr, Config) and isinstance(value, dict):
                # Recursively set nested config
                attr.__class__.from_dict(value)
                
        return instance
    
    def save(cls, file_path: str | Path) -> None:
        """Save config to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(cls.to_dict(), f, indent=4)
    
    @classmethod
    def load(cls, file_path: str | Path) -> Config:
        """Load config from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def get_all_settings(self) -> dict[str, Setting]:
        """Get all settings recursively with their full paths."""
        result = {}
        
        def collect_settings(config, prefix=""):
            for key, value in vars(config.__class__).items():
                if key.startswith('_'):
                    continue
                    
                full_path = f"{prefix}{key}" if prefix else key
                
                if isinstance(value, Setting):
                    result[full_path] = value
                elif isinstance(value, Config):
                    collect_settings(value, f"{full_path}.")
        
        collect_settings(self)
        return result
