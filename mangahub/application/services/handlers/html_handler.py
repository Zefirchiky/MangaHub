from .file_handler import FileHandler


class HtmlHandler(FileHandler[str, str]):
    def __init__(self, file):
        super().__init__(file, '.html')
        
    def load(self):
        with self.file.open('r') as f:
            return f.read()
        
    def save(self, data):
        with self.file.open('w') as f:
            f.write(data)