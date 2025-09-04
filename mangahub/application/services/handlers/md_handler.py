from .file_handler import FileHandler


class MdHandler(FileHandler[str, str]):
    def __init__(self, file):
        super().__init__(file, '.md')
        
    def load(self):
        with self.file.open() as f:
            return f.read()
        
    def save(self, data):
        with self.file.open('w', encoding='utf-8') as f:
            f.write(data)