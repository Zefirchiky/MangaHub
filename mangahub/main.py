import ctypes
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from gui import MainWindow
from gui.gui_utils import MM
from services.parsers import MangaJsonParser, SitesJsonParser
from controllers import MangaManager
from directories import *


    
class App:
    def __init__(self):
        myappid = 'mangahub.0.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.gui_app = QApplication(sys.argv)
        self.gui_app.setWindowIcon(QIcon("resources/app_icon.ico"))
        self.gui_window = MainWindow(self)
        self.message_manager = MM(self)

        self.manga_json_parser = MangaJsonParser(MANGA_JSON)
        self.sites_json_parser = SitesJsonParser(SITES_JSON)

        self.manga_manager = MangaManager(self)

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()
        
        MM.show_message('info', f"Working directory: \n{os.getcwd()}", 7000)
        
        self.gui_app.exec()


if __name__ == "__main__":
    app = App()
    app.run()