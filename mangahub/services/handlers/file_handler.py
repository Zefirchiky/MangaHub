from abc import ABC, abstractmethod
from pathlib import Path


class FileHandler[LV, SV](ABC):
    def __init__(self, file: Path):
        self.file = file

    @abstractmethod
    def load(self) -> LV:
        pass

    @abstractmethod
    def save_data(self, data: SV):
        pass