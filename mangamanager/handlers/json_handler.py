from .file_handler import FileHandler
import json

class JsonHandler(FileHandler):
    def __init__(self, file):
        super().__init__(file)
        self.data = None

    def load(self) -> None:
        with open(self.file, 'r') as f:
            self.data = json.load(f)
        return self.data

    def get_data(self) -> dict:
        return self.data if self.data is not None else self.load()

    def save_data(self, data) -> None:
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=4)