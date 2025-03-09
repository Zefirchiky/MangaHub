import json
from pathlib import Path

from .file_handler import FileHandler


class JsonHandler(FileHandler):
    def __init__(self, file: Path | str):
        if isinstance(file, str):
            file = Path(file)
            
        super().__init__(file)
        if not file.exists():
            path = file.parent
            path.mkdir(exist_ok=True)
            with file.open('w') as f:
                json.dump({}, f, indent=4)
                
        self.file = file
        self.data = None

    def load(self) -> None:
        with self.file.open('r') as f:
            self.data = json.load(f)
        return self.data

    def get_data(self) -> dict:
        return self.data if self.data is not None else self.load()

    def save_data(self, data) -> None:
        with self.file.open('w') as f:
            json.dump(data, f, indent=4)