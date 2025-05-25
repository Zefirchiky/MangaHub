from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QMainWindow, QStackedLayout, QWidget
from loguru import logger

from ui.multi_window import AddMangaWindow, SettingsWindow
from ui.widgets import IconRepo, ImageWidget, SelectionMenu
from ui.widgets.dashboard import Dashboard, MediaCard
from ui.widgets.scroll_areas import MangaViewer, NovelViewer
from ui.widgets.slide_menus import SideMenu

from models.abstract import AbstractMedia

from app_status import AppStatus
from utils import MM  # TODO
from config import Config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class MainWindow(QMainWindow):
    def __init__(self, app: "App"):
        super().__init__()
        self.app = app

        self.setWindowTitle("MangaHub")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon(str(Config.Dirs.RESOURCES / "app_icon.ico")))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        ImageWidget.set_default_placeholder(width=200, height=300)
        ImageWidget.set_default_error_image(Config.Dirs.IMAGES / "placeholder.jpg")

        IconRepo.init_default_icons()

        self.settings_is_opened = False
        self.manga_cards: dict[str, MediaCard] = {}

        # root layout
        self.root_layout = QStackedLayout()
        root = QWidget()
        root.setLayout(self.root_layout)
        self.setCentralWidget(root)

        # side menu
        self.side_menu = SideMenu(self)
        self.side_menu.add_button(
            lambda: self.root_layout.setCurrentIndex(
                0 if self.root_layout.currentIndex() != 0 else 1
            ),
            IconRepo.get(IconRepo.Icons.MANGA),
            "Manga",
            is_default=True,
        )
        self.side_menu.add_button(
            lambda: self.root_layout.setCurrentIndex(2),
            IconRepo.get(IconRepo.Icons.NOVEL),
            "Novel",
        )

        self.side_menu.set_settings_function(self.open_settings)

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)

        logger.success("MainWindow widget initialized")

    def init(self):
        self.manga_manager = self.app.manga_manager
        self.sites_manager = self.app.sites_manager
        self.app_controller = self.app.app_controller

        self.selection_menu = SelectionMenu(self)
        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow(self.app_controller)
        self.dashboard = Dashboard()
        self.manga_viewer = MangaViewer(self)
        self.novel_viewer = NovelViewer()
        # self.chapter_image_loader = self.manga_manager.chapter_loader

        self.selection_menu.show()

        self.root_layout.insertWidget(0, self.dashboard)
        self.root_layout.insertWidget(1, self.manga_viewer)
        self.root_layout.insertWidget(2, self.novel_viewer)

        for manga in self.app_controller.manga_manager.get_all():
            self.create_new_card(manga)

        self.current_mc: MediaCard | None = None

        self.init_connections()

        AppStatus.main_window_initialized = True
        logger.success("MainWindow initialized")

    def init_connections(self):
        self.app_controller.init_connections()

        self.manga_manager.cover_downloaded.connect(
            lambda manga_name, cover: self.dashboard.get_card(manga_name).set_cover(
                cover
            )
        )
        self.manga_manager.chapters_dict_downloaded.connect(
            lambda manga_name, chapters: self.dashboard.get_card(
                manga_name
            ).set_chapter_nums(self.app_controller.get_manga(manga_name))
        )

        self.app_controller.manga_created.connect(
            lambda manga: self.dashboard.add_card(self.create_new_card(manga))
        )

        self.app_controller.manga_changed.connect(self.update_current_mc)
        self.app_controller.manga_changed.connect(self.manga_viewer.set_manga)

        self.app_controller.chapter_changed.connect(self.show_manga)
        self.app_controller.chapter_changed.connect(self.update_current_mc)

        # Setting chapter
        self.manga_viewer.close_button.clicked.connect(
            lambda _: self.root_layout.setCurrentIndex(0)
        )
        self.manga_viewer.chapter_selection.activated.connect(
            lambda x: self.app_controller.set_chapter(x + 1)
        )
        self.manga_viewer.prev_button.clicked.connect(self.app_controller.prev_chapter)
        self.manga_viewer.next_button.clicked.connect(self.app_controller.next_chapter)

        self.app_controller.chapter_changed.connect(self.manga_viewer.set_chapter)

        # Connecting download to manga_viewer
        # self.app_controller.manga_chapter_placeholder_ready.connect(
        #     lambda manga, chapter, i, pixmap: self.manga_viewer.add_placeholder(
        #         i, pixmap
        #     )
        # )
        # self.app_controller.manga_chapter_image_ready.connect(
        #     lambda manga,
        #     chapter,
        #     i,
        #     name,
        #     image: self.manga_viewer.replace_placeholder(i, name)
        # )

        # self.chapter_image_loader.overall_download_progress.connect(
        #     lambda urls_num, percent, current, total: MM.show_progress(
        #         f"Images downloading for {self.app_controller.state.manga_name} {self.app_controller.state.chapter_num}",
        #         current,
        #         total,
        #         "Downloading progress",
        #         format_="%p% (%v/%t Bytes)",
        #     )
        # )  # len(urls), percent, current bytes, total bytes
        # self.chapter_image_loader.finished.connect(
        #     lambda: MM.finish_progress(
        #         f"Images downloading for {self.app_controller.state.manga_name} {self.app_controller.state.chapter_num}"
        #     )
        # )
        # self.chapter_image_loader.finished.connect(self.manga_viewer._on_chapter_loaded)
        # self.chapter_image_loader.finished.connect(
        #     lambda: MM.show_success("Images were downloaded successfully")
        # )

        # self.manga_dashboard.add_manga_button.clicked.connect(self.add_manga)

        logger.success("MainWindow connections initialized")

    def show_manga(self):
        self.manga_viewer.clear()

        manga, chapter = (
            self.app_controller.state._manga,
            self.app_controller.state._chapter,
        )

        self.app_controller.manga_manager.chapter_loader.load_chapter(
            manga.id_, chapter
        )

        self.root_layout.setCurrentIndex(1)

    def update_current_mc(self):  # TODO(?): possibly another state, just for gui
        self.current_mc = self.dashboard.get_card(self.app_controller.state.manga_name)
        self.current_mc.update_buttons()

    def create_new_card(self, media: AbstractMedia) -> MediaCard:
        mc = MediaCard()
        mc.set_media(media)
        self.dashboard.add_card(mc)
        mc.chapter_clicked.connect(self.app_controller.select_media_chapter)
        return mc

    def open_settings(self):
        self.settings_is_opened ^= 1
        if self.settings_is_opened:
            self.settings_window.show()
        else:
            self.settings_window.hide()

    def add_manga(self):
        self.add_manga_window.show()
        self.add_manga_window.add_manga_button.clicked.connect(
            lambda _: self.dashboard.add_card(
                self.manga_manager.get_manga(self.add_manga_window.name_input.text())
            )
        )

    def check_mouse_position(self):
        cursor_pos = QCursor.pos()
        window_pos = self.mapToGlobal(QPoint(0, 0))
        if (
            0
            <= cursor_pos.x() - window_pos.x()
            <= self.side_menu.x() + self.side_menu._width
        ):
            if self.root_layout.currentIndex() != 2:
                self.side_menu.show_menu()
            else:
                if cursor_pos.x() - window_pos.x() <= self.side_menu._width - 20:
                    self.side_menu.show_menu()
        elif (
            self.side_menu.x() + self.side_menu._width
            < cursor_pos.x() - window_pos.x()
            <= self.side_menu._width + 400
        ):
            self.side_menu.show_half_menu()
        else:
            self.side_menu.hide_menu()

    def resizeEvent(self, event):
        self.side_menu.adjust_geometry()
        MM().pos_update()

        return super().resizeEvent(event)

    def closeEvent(self, event):
        self.settings_window.close()
        self.add_manga_window.close()
        self.app_controller.save()
        return super().closeEvent(event)
