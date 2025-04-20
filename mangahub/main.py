import ctypes
import sys

from directories import (
    IMAGES_CACHE_DIR,
    MANGA_JSON,
    NOVELS_CONF_DIR,
    NOVELS_JSON,
    RESOURCES_DIR,
    SITES_JSON,
    STD_DIR,
    CONF_FILE,
)
from config import CM
from controllers import AppController, MangaManager, NovelsManager, SitesManager
from ui import MainWindow
from ui.widgets import IconRepo
from loguru import logger
from icecream import ic
from models.novels import NovelFormatter
from models.manga import ChapterImage
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from services.handlers import JsonHandler
from services.parsers import SitesParser, UrlParser
from services.repositories import MangaRepository, NovelsRepository
from config import AppConfig
from utils import MM

ic(f"MangaHub v{AppConfig.version()}")
logger.info(f"Working directory: {STD_DIR}")


class App:
    def __init__(self):
        logger.debug(f"MangaHub v{AppConfig.version()}")
        logger.info(f"Starting MangaHub v{AppConfig.version()}")

        myappid = f"mangahub.{AppConfig.version()}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.gui_app = QApplication(sys.argv)
        self.gui_app.setWindowIcon(QIcon(f"{RESOURCES_DIR}/app_icon.ico"))
        self.gui_window = MainWindow(self)
        self.message_manager = MM(self)
        self.color_manager = CM(self)
        self.icon_repository = IconRepo()

        # Set defaults
        NovelFormatter.global_replaces = JsonHandler(
            f"{NOVELS_CONF_DIR}/global_replace.json"
        ).load()

        self.sites_json_parser = SitesParser(SITES_JSON)
        UrlParser.set_parser(self.sites_json_parser)
        self.sites_manager = SitesManager(self)

        self.manga_repository = MangaRepository(MANGA_JSON)
        self.manga_manager = MangaManager(self)

        self.novels_repository = NovelsRepository(NOVELS_JSON)
        self.novels_manager = NovelsManager(self)

        self.app_controller = AppController(self)

        # from models.sites import SiteChapterPage, SiteTitlePage, LastChapterParsingMethod
        # from models.manga import ImageParsingMethod
        # self.sites_manager.create_site("AsuraScans", "https://asuracomic.net",
        #                                    SiteChapterPage(url_format="series/$manga_id$-$num_identifier$/chapter/$chapter_num$"),
        #                                    ImageParsingMethod().set_regex_from_html('https://gg\\.asuracomic\\.net/storage/media/\\d{6}/conversions/\\d{2}-optimized\\.webp'),
        #                                    LastChapterParsingMethod(string_format="$manga_id$-$num_identifier$/chapter/$chapter_num$", on_title_page=True),
        #                                    title_page=SiteTitlePage(url_format="series/$manga_id$-$num_identifier$"),
        #                                    num_identifier="ffffffff")

        # self.app_controller.create_manga("Boundless Necromancer", site="AsuraScans")
        # self.app_controller.create_manga("Nano Machine", site="AsuraScans")
        # self.app_controller.create_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!")
        # self.app_controller.create_manga("Dragon-Devouring Mage")
        # self.app_controller.create_manga("Hero? I Quit A Long Time Ago")
        # self.app_controller.remove_manga('Dragon-Devouring Mage')
        # self.app_controller.remove_manga('return of the disaster class hero')
        # self.app_controller.remove_manga(self.app_controller.get_manga('Circles'))
        # self.app_controller.remove_manga('Bad Born Blood')
        # self.app_controller.get_manga('I, The Demon Lord, Am Being Targeted by My Female Disciples!').description = 'lol'
        self.test_code()

    def test_code(self): ...

    def run(self):
        self.gui_window.showMaximized()
        self.gui_window.init()

        MM.show_info(f"Working directory: \n{STD_DIR}", 7000)

        logger.success(f"MangaHub v{AppConfig.version()} initialized")
        self.gui_app.exec()

        # AppConfig().save(CONF_FILE)
        logger.success("AppConfig was saved successfully")

        logger.info(f"MangaHub v{AppConfig.version()} finished")


if __name__ == "__main__":
    app = App()
    app.run()
