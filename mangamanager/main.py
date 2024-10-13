from PySide6.QtWidgets import QApplication
from gui import MainWindow
from services.parsers import MangaJsonParser
from controllers.manga_manager import MangaManager

import os

class App:
    def __init__(self):
        self.dir = os.path.dirname(__file__)
        self.gui_app = QApplication([])

        manga = MangaManager().get_manga_from_url("https://asuracomic.net/series/raising-the-princess-to-overcome-death-a387da1a")
        print(manga)

        self.gui_window = MainWindow()

    def run(self):
        self.gui_window.showMaximized()
        self.gui_app.exec()

if __name__ == "__main__":
    app = App()
    app.run()