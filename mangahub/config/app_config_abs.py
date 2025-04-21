from __future__ import annotations
from typing import Type, Protocol
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Flag, auto
import typing
import json
from models.abstract import TypeEnforcer


# JSON serializable primitive types
type JsonPrimitiveTypes = str | int | float | bool | None

# This is a type alias for all types that can be serialized to JSON
type JsonSerializableTypes = (
    JsonPrimitiveTypes | dict[typing.Any, typing.Any] | list[typing.Any]
)


class SettingValue(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def from_dict(self, dict_: dict):
        pass


class SettingValueProtocol(Protocol):
    def to_dict(self) -> dict: ...

    @abstractmethod
    def from_dict(self, dict_: dict): ...



class Level(Flag):
    USER = auto()
    USER_DEV = auto()   # For users with dev_mode
    DEVELOPER = auto()  # For plugin developers
    ADVANCED = auto()
    READ_ONLY = auto()
    HIDDEN = auto()
    
class SettingType(Flag):
    PERFORMANCE = auto()
    COSMETIC = auto()
    QOL = auto()
    OTHER = auto()

class Setting[T: SettingValue | SettingValueProtocol | JsonSerializableTypes](
    TypeEnforcer[T]
):
    JsonSerializableTypes = JsonSerializableTypes
    SettingValue = SettingValue
    SettingValueProtocol = SettingValueProtocol
    
    Level = Level
    SettingType = SettingType

    def __init__(
        self,
        value: T,
        name: str = "",
        unit: str = "",     # TODO: Better units
        options=None,
        level: Level=Level.USER,
        type_: SettingType=SettingType.OTHER,
        description="",
        strongly_typed: bool = True,
    ):
        """Class to create setting in the Config. Is strongly typed.
        Create with `Setting[value_type](value)`.

        Value type must either be `Setting.SettingValue`, of `Setting.JsonSerializableTypes` type or use `Setting.SettingValueProtocol`

        By default Setting will not try parsing `value` into instance of `value_type`. Set `strongly_typed` to `False` to change it.

        Value of the class can be accessed by calling the instance:

        ```number = Setting[int](15, 'Some Number')
        number()   # returns a number._value (15)
        ```
        """
        super().__init__(value, strongly_typed)
        self.name = name
        self.unit = unit
        self.options = options
        self.level = level
        self.type_ = type_
        self.description = description

        self._type: Type[T] | None = None

    def __call__(self) -> T:
        return self._value

    def __set__(self, instance, value: T) -> None:
        self._check_type(value, self._type)

    def __str__(self) -> str:
        return f"{self.name}: {self._type.__name__}({self()}{f' {self.unit}' if self.unit else ''})"    # type: ignore

    # def to_dict(self) -> dict[str, typing.Any]:
    #     """Convert setting to dictionary."""
    #     return {"value": self._value.to_dict, "name": self.name, "description": self.description}


class ConfigMeta(type):
    """Metaclass for Config to enable proper inheritance and access patterns."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Type:
        cls = super().__new__(mcs, name, bases, namespace)
        setattr(cls, '_config_name', name)

        # Process nested Config classes to make them proper attributes
        for key, value in list(cls.__dict__.items()):
            if (
                isinstance(value, type)
                and issubclass(value, Config)
                and value is not Config
            ):
                # Replace the class reference with an instance
                setattr(cls, key, value())

        return cls


class Config(metaclass=ConfigMeta):
    """Base configuration class."""

    def to_dict(self) -> dict[str, typing.Any]:
        """Convert config to dictionary recursively."""
        result = {}

        # Process all attributes including inherited ones
        for key, value in vars(self.__class__).items():
            if key.startswith("_"):
                continue

            if isinstance(value, Setting):
                if hasattr(value(), "to_dict") and callable(value().to_dict):
                    result[key] = value().to_dict()
                else:
                    result[key] = value()
            elif isinstance(value, Config):
                result[key] = value.to_dict()

        return result

    # def to_dict_with_metadata(self) -> dict[str, ]:   # TODO: May be

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> Config:
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

    def save(self, file_path: str | Path) -> None:
        """Save config to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, file_path: str | Path) -> Config:
        """Load config from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_settings_dict(self) -> dict[str | Config, Setting]:
        result = {}

        for key, value in vars(self.__class__).items():
            if key.startswith("_"):
                continue

            if isinstance(value, Setting):
                result[key] = value
            elif isinstance(value, Config):
                result[key] = value.get_settings_dict()

        return result

    def get_all_settings(self) -> dict[str, Setting]:
        """Get all settings recursively with their full paths."""
        result = {}

        def collect_settings(config, prefix=""):
            for key, value in vars(config.__class__).items():
                if key.startswith("_"):
                    continue

                full_path = f"{prefix}{key}" if prefix else key

                if isinstance(value, Setting):
                    result[full_path] = value
                elif isinstance(value, Config):
                    collect_settings(value, f"{full_path}.")

        collect_settings(self)
        return result

    def __str__(self) -> str:
        def handle_dict(dict_: dict[str, Setting | dict], indent: int = 1) -> str:
            s = ""
            for key, value in dict_.items():
                if isinstance(value, dict):
                    s += "  " * indent + f"{key}:\n"
                    s += handle_dict(value, indent + 1)
                else:
                    s += "  " * indent + f"{value._attribute_name}: {str(value)}\n"
            return s

        return f"{self._config_name}:\n" + handle_dict(self.get_settings_dict())
