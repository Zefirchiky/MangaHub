import ctypes
import asyncio
import sys
import os

from config import CM
from controllers import AppController, MangaManager, NovelsManager, SitesManager
from ui import MainWindow
from ui.widgets import IconRepo
from loguru import logger
from models.novels import NovelFormatter
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
import PySide6.QtCore
from services.downloaders import DownloadManager
from services.handlers import JsonHandler
from services.repositories.manga import MangaRepository
from services.repositories.novels import NovelsRepository
from config import Config
from utils import MM


logger.info(f"Working directory: {Config.Dirs.STD_DIR}")


class App:
    def __init__(self):
        logger.debug(f"MangaHub v{Config.version()}")
        logger.info(f"Starting MangaHub v{Config.version()}")

        logger.info(f"PySide6 version: {PySide6.__version__}")
        logger.info(f"PySide6.QtCore version: {PySide6.QtCore.__version__}")
        
        myappid = f"mangahub.{Config.version()}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.gui_app = QApplication(sys.argv)
        self.gui_app.setWindowIcon(QIcon(f"{Config.Dirs.RESOURCES}/app_icon.ico"))
        self.gui_window = MainWindow(self)
        self.message_manager = MM(self)
        self.color_manager = CM(self)
        self.icon_repository = IconRepo()

        # Set defaults
        NovelFormatter.global_replaces = JsonHandler(
            f"{Config.Dirs.NOVELS_CONF}/global_replace.json"
        ).load()

        self.sites_manager = SitesManager()
        
        self.download_manager = DownloadManager(self)

        self.manga_repository = MangaRepository(Config.Dirs.MANGA_JSON)
        self.manga_manager = MangaManager(self)

        self.novels_repository = NovelsRepository(Config.Dirs.NOVELS_JSON)
        self.novels_manager = NovelsManager(self)

        self.app_controller = AppController(self)

        # from models.sites.parsing_methods import (
        #     MangaParsing,
        #     NameParsing,
        #     CoverParsing,
        #     ChaptersListParsing,
        #     MangaChapterParsing,
        #     ImagesParsing
        # )

        # self.sites_manager.create_site(
        #     "AsuraScans",
        #     "https://asuracomic.net",
        #     MangaParsing(
        #         name_parsing=NameParsing(
        #             path="series/{media_id}-6905f93c",
        #             name="span",
        #             look_for='text',
        #             class_="text-xl font-bold",
        #         ),
        #         cover_parsing=CoverParsing(
        #             path="series/{media_id}-6905f93c",
        #             name="img",
        #             look_for="src",
        #             class_="rounded mx-auto md:mx-0",
        #             alt="poster"
        #         ),
        #         last_chapter_parsing=ChaptersListParsing(
        #             path="series/{media_id}-6905f93c",
        #             name="div",
        #             class_="pl-4 pr-2 pb-4 overflow-y-auto scrollbar-thumb-themecolor scrollbar-track-transparent scrollbar-thin mr-3 max-h-[20rem] space-y-2.5"
        #         ).add_parsing_method(
        #             ChaptersListParsing(
        #                 regex=r'/chapter/(\d+)'
        #             )
        #         ),
        #     ),
        #     MangaChapterParsing(
        #         images_parsing=ImagesParsing(
        #             path="series/{media_id}-6905f93c/chapter/{chapter_num}",
        #             name="script",
        #             regex=r"https://gg\.asuracomic\.net/storage/media/\d+/conversions/\d+-optimized.webp",
        #         ),
        #     )
        # )

        # self.app_controller.create_manga("Return From The Abyss", site="AsuraScans", overwrite=True)
        # self.app_controller.create_manga("Boundless Necromancer", site="AsuraScans", overwrite=True)
        # self.app_controller.create_manga("The Extra's Academy Survival Guide", site="AsuraScans")
        # self.app_controller.create_manga("Nano Machine", site="AsuraScans")
        # self.app_controller.create_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!")
        # self.app_controller.create_manga("Dragon-Devouring Mage", site="AsuraScans")
        # self.app_controller.create_manga("Hero? I Quit A Long Time Ago")
        
        # self.app_controller.remove_manga('Dragon-Devouring Mage')
        # self.app_controller.remove_manga('return of the disaster class hero')
        # self.app_controller.remove_manga(self.app_controller.get_manga('Circles'))
        # self.app_controller.remove_manga('Bad Born Blood')
        
        # self.app_controller.get_manga('I, The Demon Lord, Am Being Targeted by My Female Disciples!').description = 'lol'
        
        self.test_code()

    def test_code(self):
        # from services.downloaders import HtmlDownloader
        # self.jh = JsonHandler('test_json')
        # self.mh = HtmlHandler('test_md')
        # self.d = HtmlDownloader()
        # self.d.finished.connect(lambda url, text: HtmlHandler.fast_save(Path(url.replace('/', '-').replace(':', '-')).resolve(), text))
        # self.d.get_htmls([
        #     'https://stackoverflow.com/questions/862412/is-it-possible-to-have-multiple-statements-in-a-python-lambda-expression',
        #     'https://doc.qt.io/qtforpython-6/PySide6/QtCore/QRunnable.html#PySide6.QtCore.QRunnable'
        #     ])

        pass

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()

        MM.show_info(f"Working directory: \n{Config.Dirs.STD_DIR}", 7000)
        MM.show_progress("lol1", 12, 100, "lol", format_="%p% (%v/%t Bytes)")

        logger.success(f"MangaHub v{Config.version()} initialized")
        self.gui_app.exec()

        # AppConfig().save(CONF_FILE)
        logger.success("AppConfig was saved successfully")

        logger.info(f"MangaHub v{Config.version()} finished")


if __name__ == "__main__":
    app = App()
    app.run()
