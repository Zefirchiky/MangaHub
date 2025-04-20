from __future__ import annotations
from typing import (
    Any,
    Type,
    Sequence,
    Set,
    MutableSet,
    MutableSequence,
    Mapping,
    MutableMapping,
    get_type_hints,
    get_origin,
    get_args,
)
from types import UnionType


class TypeEnforcer[T]:
    """Class will enforce `T` type on `value`"""

    def __init__(
        self, value: T, strongly_typed: bool = True, try_parse_after_failure=False
    ):
        """
        Args:
            value (T): value to be enforced
            strongly_typed (bool, optional): If set to `True`, will immediately raise a TypeError if value's type is wrong.
            Otherwise, will try to parse the value by invoking T(value). Defaults to True.
            try_parse_after_failure (bool, optional): Will try to parse all values even if parsing of one failed. Defaults to False.
        """
        self._value = value
        self.strongly_typed = strongly_typed
        self.try_parse_after_error = try_parse_after_failure

    def __set_name__(self, owner: Type, name: str):
        """Called when the TypeEnforcer is declared in a class."""
        self._attribute_owner = owner
        self._attribute_name = name

        if hasattr(self, "__orig_class__"):
            origin = get_origin(self.__orig_class__)
            args = get_args(self.__orig_class__)
        elif name in (hints := get_type_hints(owner)):
            origin = get_origin(hints[name])
            args = get_args(origin)
        else:
            raise TypeError("Type must be set, either in type hint, or in generic type")

        if origin and args:
            self._type = args[0]

        if self.strongly_typed or isinstance(self._value, (tuple, frozenset)):
            parsed = self._check_type(self._value, self._type)
            val = None
        else:
            parsed, val = self._parse_check_type(
                self._value, self._type, self.try_parse_after_error
            )

        if parsed:
            if val is not None:
                self._value = val
        else:
            if self.strongly_typed:
                raise TypeError(
                    f"Value of class {owner}.{name} must be of type {self._type}"
                )
            else:
                raise TypeError(
                    f"Value of class {owner}.{name} must be of type {self._type} or corresponding values must be able to convert into corresponding types.\n"
                    f"Unable to convert {self._value} in type {self._type}"
                )

    @classmethod
    def _check_type(cls, value, type_) -> bool:
        """
        Checks if the value is of the given type.

        Args:
            `value`: The value to check.
            `type_`: The type to check against.

        Returns:
            True if the value is of the given type, False otherwise.
        """
        orig = get_origin(type_)
        args = get_args(type_)

        # Is simple type (aka int, str)
        if not orig:
            return isinstance(value, type_)

        # Is union (aka int | str)
        elif orig is UnionType:
            return any(cls._check_type(value, arg) for arg in args)

        # Is complex type (aka dict[str, int], list[dict[str, str | int]])
        else:
            if isinstance(value, orig):
                if isinstance(value, list) or issubclass(
                    orig, (Sequence, MutableSequence)
                ):
                    return all(map(lambda x: cls._check_type(x, args[0]), value))

                if isinstance(value, dict) or issubclass(
                    orig, (Mapping, MutableMapping)
                ):
                    return all(
                        map(lambda x: cls._check_type(x, args[0]), value.keys())
                    ) and all(
                        map(lambda x: cls._check_type(x, args[1]), value.values())
                    )

            else:
                return False

        raise TypeError(f"Type '{type_}' is not supported yet")

    @classmethod
    def _parse_check_type(
        cls, value, type_, ignore_error=False
    ) -> tuple[bool, T | Any]:
        """
        Attempts to parse a value to a specified type, supporting complex and union types.

        This method checks whether a given value can be parsed into the specified type.
        If the value is not of the specified type, it attempts to convert it. The method
        supports simple types, union types, sequences, set, and mappings. If the conversion
        is successful, it returns the parsed value; otherwise, it returns the failed value,
        see `ignore_error`.

        Args:
            `value`: The value to be checked and potentially parsed.
            `type_`: The target type to parse the value into.
            `ignore_error` (bool, optional): If set to True, the method will attempt to parse
                                        all elements in sequences and mappings even if
                                        parsing of one element fails. Defaults to False.

        Returns:
            A tuple where the first element is a boolean indicating if the parsing was
            successful, and the second element is the parsed value or the original value
            if parsing was unsuccessful.
        """

        orig = get_origin(type_)
        args = get_args(type_)

        # Is simple type (aka int, str)
        if not orig:
            if not isinstance(value, type_):
                try:
                    return True, type_(value)
                except (ValueError, TypeError):
                    return False, value
            return True, value

        # Is union (aka int | str)
        elif orig is UnionType:
            for arg in args:
                parsed, v = cls._parse_check_type(value, arg, ignore_error)
                if parsed:
                    break
            return parsed, v

        # Is complex type (aka dict[str, int], list[dict[str, str | int]])
        else:
            if isinstance(value, orig):
                if is_list := isinstance(value, list) or issubclass(
                    orig, (Sequence, MutableSequence, Set, MutableSet)
                ):
                    result_list = []
                    parsed = True
                    for v in value:
                        values_parsed, val = cls._parse_check_type(
                            v, args[0], ignore_error
                        )
                        result_list.append(val)
                        if not values_parsed:
                            parsed = False
                            if not ignore_error:
                                break
                    return parsed, result_list if is_list else type(value)(result_list)

                if isinstance(value, dict) or issubclass(
                    orig, (Mapping, MutableMapping)
                ):
                    result_dict = {}
                    parsed = True
                    for k, v in value.items():
                        keys_parsed, key = cls._parse_check_type(
                            k, args[0], ignore_error
                        )
                        values_parsed, val = cls._parse_check_type(
                            v, args[1], ignore_error
                        )
                        result_dict[key] = val
                        if not keys_parsed or not values_parsed:
                            parsed = False
                            if not ignore_error:
                                break
                    return parsed, result_dict

            else:
                return False, value
