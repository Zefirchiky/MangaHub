from .file_handler import FileHandler
import json
import os

class JsonHandler(FileHandler):
    def __init__(self, file):
        super().__init__(file)
        if not os.path.exists(self.file):
            path, name = os.path.split(self.file)
            os.makedirs(path, exist_ok=True)
            with open(self.file, 'w') as f:
                json.dump({}, f, indent=4)
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