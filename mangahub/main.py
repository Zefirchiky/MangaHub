from PySide6.QtWidgets import QApplication
from gui import MainWindow
from gui.utils import MessageManager
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from controllers import MangaManager
from directories import *
from utils import retry


    
class App:
    def __init__(self):
        self.gui_app = QApplication([])
        self.gui_window = MainWindow(self)
        self.mm = MessageManager(self)

        self.manga_json_parser = MangaJsonParser(MANGA_JSON)
        self.sites_json_parser = SitesJsonParser(SITES_JSON)

        self.manga_manager = MangaManager(self)

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()
        
        self.mm.show_message('info', os.getcwd())
        self.gui_app.exec()


if __name__ == "__main__":
    app = App()
    app.run()