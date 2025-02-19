from PySide6.QtWidgets import (
    QMainWindow,
    QStackedLayout, 
    QWidget
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QCursor, QIcon
from loguru import logger

from gui.multi_window import AddMangaWindow, SettingsWindow
from gui.widgets.scroll_areas import MangaViewer, MangaDashboard, NovelViewer
from gui.widgets.slide_menus import SideMenu
from gui.widgets import SvgIcon, SelectionMenu, ImageWidget
from utils import MM
from controllers import SitesManager, MangaManager, AppController
from app_status import AppStatus
from directories import *


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("MangaHub")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon(str(RESOURCES_DIR / "app_icon.ico")))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        ImageWidget.set_default_placeholder(width=200, height=300)
        ImageWidget.set_default_error_image(IMAGES_DIR / "placeholder.jpg")
        
        self.settings_is_opened = False
        self.manga_cards = {}
        

        # root layout
        self.root_layout = QStackedLayout()
        root = QWidget()
        root.setLayout(self.root_layout)
        self.setCentralWidget(root)


        # side menu
        book_svg_icon = QIcon(str(ICONS_DIR / "comic.png"))
        novel_svg_icon = SvgIcon(ICONS_DIR / "novel.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(0), book_svg_icon, "Manga", is_default=True)
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(2), novel_svg_icon, "Novel")

        self.side_menu.set_settings_function(self.open_settings)

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)

        logger.success('MainWindow widget initialized')
        
    def init(self):
        self.manga_manager: MangaManager = self.app.manga_manager
        self.sites_manager: SitesManager = self.app.sites_manager
        self.app_controller: AppController = self.app.app_controller
        
        self.selection_menu = SelectionMenu(self)
        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow(self.app_controller)
        self.manga_dashboard = MangaDashboard()
        self.manga_viewer = MangaViewer()
        self.novel_viewer = NovelViewer()

        self.selection_menu.show()
        
        self.root_layout.insertWidget(0, self.manga_dashboard)
        self.root_layout.insertWidget(1, self.manga_viewer)
        self.root_layout.insertWidget(2, self.novel_viewer)
        
        for manga in self.app_controller.manga_manager.get_all_manga().values():
            mc = self.manga_dashboard.add_manga(manga)
            mc.chapter_clicked.connect(self.app_controller.select_manga_chapter)

        self.init_connections()
        
        AppStatus.main_window_initialized = True
        logger.success('MainWindow initialized')
        
    def init_connections(self):
        self.app_controller.init_connections()
        
        self.app_controller.chapter_changed.connect(self.show_manga)
        self.app_controller.chapter_changed.connect(self.manga_viewer.set_chapter)
        self.app_controller.chapter_changed.connect(lambda _: self.manga_dashboard.update_manga(self.app_controller.manga_state._manga))
        self.app_controller.manga_changed.connect(self.manga_viewer.set_manga)
        
        self.manga_viewer.close_button.clicked.connect(lambda _: self.root_layout.setCurrentIndex(0))
        self.manga_viewer.chapter_selection.activated.connect(lambda x: self.app_controller.select_chapter(x + 1))
        self.manga_viewer.prev_button.clicked.connect(self.app_controller.select_prev_chapter)
        self.manga_viewer.next_button.clicked.connect(self.app_controller.select_next_chapter)
        
        self.manga_dashboard.add_manga_button.clicked.connect(self.add_manga)
        
        logger.success('MainWindow connections initialized')
        
    def show_manga(self):
        self.manga_viewer.clear()
        
        placeholders = self.app_controller.get_manga_chapter_placeholders()
        worker = self.manga_manager.get_chapter_images()
        
        self.manga_viewer.prev_button.setEnabled(not self.app_controller.manga_state.is_first())
        self.manga_viewer.next_button.setEnabled(not self.app_controller.manga_state.is_last())
    
        current_y = 0
        for width, height in placeholders:
            self.manga_viewer.add_placeholder(width, height, current_y)
            current_y += height + self.manga_viewer._vertical_spacing
        
        worker.signals.item_completed.connect(lambda r: self.manga_viewer.replace_placeholder(r[0], r[1].content))
        self.app_controller.manga_state.set_worker(worker)
        
        self.root_layout.setCurrentIndex(1)

    def open_settings(self):
        self.settings_is_opened ^= 1
        if self.settings_is_opened:
            self.settings_window.show()
        else:
            self.settings_window.hide()

    def add_manga(self):
        self.add_manga_window.show()
        self.add_manga_window.add_manga_button.clicked.connect(
            lambda _: self.manga_dashboard.add_manga(
                self.manga_manager.get_manga(self.add_manga_window.name_input.text())
                )
            )

    def check_mouse_position(self):
        cursor_pos = QCursor.pos()
        window_pos = self.mapToGlobal(QPoint(0, 0))
        if 0 <= cursor_pos.x() - window_pos.x() <= self.side_menu._width + 40:
            if self.root_layout.currentIndex() != 2:
                self.side_menu.show_menu()
            else:
                if cursor_pos.x() - window_pos.x() <= self.side_menu._width - 20:
                    self.side_menu.show_menu()
        elif self.side_menu._width + 40 < cursor_pos.x() - window_pos.x() <= self.side_menu._width + 400:
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