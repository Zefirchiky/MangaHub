from abc import ABC, abstractmethod

class FileHandler(ABC):
    def __init__(self, file):
        self.file = file

    @abstractmethod
    def load(self):
        pass

    def get_data(self):
        return self.data if self.data is not None else self.load()

    @abstractmethod
    def save_data(self):
        pass