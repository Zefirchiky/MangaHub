from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui import MainWindow
from gui.gui_utils import MessageManager
from services.parsers import MangaJsonParser, SitesJsonParser, UrlParser
from controllers import MangaManager
from directories import *
from utils import retry
import ctypes
import sys


    
class App:
    def __init__(self):
        myappid = 'none.mangahub.none.0.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.gui_app = QApplication(sys.argv)
        self.gui_app.setWindowIcon(QIcon("resources/app_icon.ico"))
        self.gui_window = MainWindow(self)
        self.mm = MessageManager(self)

        self.manga_json_parser = MangaJsonParser(MANGA_JSON)
        self.sites_json_parser = SitesJsonParser(SITES_JSON)

        self.manga_manager = MangaManager(self)

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()
        
        self.mm.show_message('info', f"Working directory: os.getcwd()", 7000)
        self.gui_app.exec()


if __name__ == "__main__":
    app = App()
    app.run()