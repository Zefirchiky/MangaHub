from PySide6.QtWidgets import QApplication
from gui import MainWindow
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from controllers import MangaManager
from directories import *


class App:
    def __init__(self):
        self.gui_app = QApplication([])

        manga_json_parser = MangaJsonParser(MANGA_JSON)
        self.sites_json_parser = SitesJsonParser(SITES_JSON)

        manga_manager = MangaManager(manga_json_parser, self.sites_json_parser)

        self.gui_window = MainWindow(self, manga_manager)

    def run(self):
        self.gui_window.showMaximized()
        self.gui_app.exec()

if __name__ == "__main__":
    app = App()
    app.run()