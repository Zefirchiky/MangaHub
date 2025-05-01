from __future__ import annotations


class StorageUnit:
    """Enhanced class for storage unit constants"""

    def __init__(self, bytes_value: int | StorageUnit | StorageSize, name: str):
        self.bytes_value = (
            bytes_value if isinstance(bytes_value, int) else bytes_value.bytes_value
        )
        self.name = name

    def __rmul__(self, other):
        """Support for operations like 100*MB"""
        if isinstance(other, (int, float)):
            return StorageSize(self.bytes_value * other)
        return NotImplemented

    def __mul__(self, other):
        """Support for operations like MB*100"""
        if isinstance(other, (int, float)):
            return StorageSize(self.bytes_value * other)
        return NotImplemented

    def __str__(self):
        return self.name


class StorageSize:
    """Class representing a specific storage size"""

    def __init__(self, bytes_value: float | int | StorageSize = 0):
        self.bytes_value = (
            int(bytes_value)
            if not isinstance(bytes_value, StorageSize)
            else bytes_value.bytes_value
        )

    def __int__(self):
        return int(self.bytes_value)

    def __float__(self):
        return float(self.bytes_value)

    def __add__(self, other):
        if isinstance(other, StorageSize):
            return StorageSize(self.bytes_value + other.bytes_value)
        elif isinstance(other, (int, float)):
            return StorageSize(self.bytes_value + other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, StorageSize):
            return StorageSize(self.bytes_value + other.bytes_value)
        elif isinstance(other, (int, float)):
            return StorageSize(self.bytes_value + other)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, StorageSize):
            return StorageSize(self.bytes_value - other.bytes_value)
        elif isinstance(other, (int, float)):
            return StorageSize(self.bytes_value - other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return StorageSize(self.bytes_value * other)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value / other.bytes_value
        elif isinstance(other, (int, float)):
            return StorageSize(self.bytes_value / other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value < other.bytes_value
        elif isinstance(other, (int, float)):
            return self.bytes_value < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value <= other.bytes_value
        elif isinstance(other, (int, float)):
            return self.bytes_value <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value > other.bytes_value
        elif isinstance(other, (int, float)):
            return self.bytes_value > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value >= other.bytes_value
        elif isinstance(other, (int, float)):
            return self.bytes_value >= other
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, StorageSize):
            return self.bytes_value == other.bytes_value
        elif isinstance(other, (int, float)):
            return self.bytes_value == other
        return NotImplemented

    def __str__(self):
        """Human-readable representation"""
        units = [
            (SU.PB.bytes_value, "PB"),
            (SU.TB.bytes_value, "TB"),
            (SU.GB.bytes_value, "GB"),
            (SU.MB.bytes_value, "MB"),
            (SU.KB.bytes_value, "KB"),
            (1, "bytes"),
        ]

        for unit_value, unit_name in units:
            if self.bytes_value >= unit_value:
                value = self.bytes_value / unit_value
                if unit_name == "bytes":
                    return f"{int(value)} {unit_name}"
                else:
                    return f"{value:.2f} {unit_name}"

        return f"{self.bytes_value} bytes"

    def __repr__(self):
        return f"StorageSize({self.bytes_value})"

    def to_dict(self) -> dict[str, int | float]:
        return {"value": self.bytes_value}

    def from_dict(self, dict_) -> None:
        self.bytes_value = dict_["value"]


class SU:
    # Define unit constants
    B = StorageUnit(1, "B")
    KB = StorageUnit(1024, "KB")
    MB = StorageUnit(1024**2, "MB")
    GB = StorageUnit(1024**3, "GB")
    TB = StorageUnit(1024**4, "TB")
    PB = StorageUnit(1024**5, "PB")

    # SI (base-10) units
    KB_SI = StorageUnit(1000, "KB")
    MB_SI = StorageUnit(1000**2, "MB")
    GB_SI = StorageUnit(1000**3, "GB")
    TB_SI = StorageUnit(1000**4, "TB")
    PB_SI = StorageUnit(1000**5, "PB")
