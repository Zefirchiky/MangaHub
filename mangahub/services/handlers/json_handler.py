import json
from pathlib import Path

from .file_handler import FileHandler


class JsonHandler(FileHandler[dict, dict]):
    def __init__(self, file: Path | str):
        super().__init__(file, '.json')

    def _create_empty(self, file):
        with file.open("w") as f:
            json.dump({}, f, indent=4)
    
    def load(self) -> dict:
        with self.file.open("r") as f:
            return json.load(f)

    def save(self, data):
        with self.file.open("w") as f:
            json.dump(data, f, indent=4)
