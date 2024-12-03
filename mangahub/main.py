import ctypes
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from modules_init import *
__builtins__.print = rich_print # Use rich print as a default

from gui import MainWindow
from gui.gui_utils import MM
from services.parsers import MangaParser, SitesParser, UrlParser
from controllers import MangaManager, SitesManager, AppController
from directories import *

VERSION = '0.1.0'


class App:
    def __init__(self):
        self.console = rich.console.Console()
        self.console.print(f"MangaHub v{VERSION}", style="bold cyan")
        logger.info(f"Starting MangaHub v{VERSION}")
        logger.info(f"Working directory: {STD_DIR}")
        
        myappid = f'mangahub.{VERSION}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        self.gui_app = QApplication(sys.argv)
        self.gui_app.setWindowIcon(QIcon(f"{RESOURCES_DIR}/app_icon.ico"))
        self.gui_window = MainWindow(self)
        self.message_manager = MM(self)

        self.manga_json_parser = MangaParser(MANGA_JSON)
        self.sites_json_parser = SitesParser(SITES_JSON)
        UrlParser.set_parser(self.sites_json_parser)

        self.sites_manager = SitesManager(self)
        self.manga_manager = MangaManager(self)
        self.app_controller = AppController(self)

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()
        
        MM.show_message('info', f"Working directory: \n{STD_DIR}", 7000)
        
        logger.success(f"MangaHub v{VERSION} initialized")
        self.gui_app.exec()
        logger.info(f"MangaHub v{VERSION} finished") 


if __name__ == "__main__":
    app = App()
    app.run()