from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout, QStackedLayout, 
    QWidget, QPushButton, QLabel
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QCursor, QIcon

from .multi_window.add_manga import AddMangaWindow
from .multi_window.settings import SettingsWindow
from .widgets.scroll_areas import MangaViewer, MangaDashboard
from .widgets.slide_menus import SideMenu
from .widgets.svg import SvgIcon
from controllers import MangaManager
from models import MangaState
from gui.gui_utils import MM
from directories import *


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("MangaHub")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("resources/app_icon.ico"))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.settings_is_opened = False
        self.manga_cards = {}
        

        # root layout
        self.root_layout = QStackedLayout()
        root = QWidget()
        root.setLayout(self.root_layout)
        self.setCentralWidget(root)


        # side menu
        book_svg_icon = SvgIcon(f"{ICONS_DIR}/book-outline.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(0), book_svg_icon, "Manga", is_default=True)

        self.side_menu.set_settings_function(self.open_settings)

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)
        
    def init(self):        
        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow()
        
        self.manager: MangaManager = self.app.manga_manager
        
        self.manga_dashboard = MangaDashboard()
        self.manga_dashboard.add_manga_button.clicked.connect(self.add_manga)
        
        self.manga_state = MangaState()
        self.manga_state._signals.manga_changed.connect(lambda _: self.show_manga())
        self.manga_state._signals.manga_changed.connect(lambda _: self.manga_viewer.set_manga(self.manga_state._manga))
        self.manga_state._signals.chapter_changed.connect(lambda _: self.show_manga())
        self.manga_state._signals.chapter_changed.connect(lambda _: self.manga_dashboard.update_manga(self.manga_state._manga))
        self.manga_state._signals.chapter_changed.connect(lambda _: self.manga_viewer.set_chapter(self.manga_state.chapter))
        
        self.manga_viewer = MangaViewer()
        self.manga_viewer.close_button.clicked.connect(lambda _: self.root_layout.setCurrentIndex(0))
        self.manga_viewer.chapter_selection.activated.connect(lambda x: self.manga_state.set_chapter(x + 1))
        self.manga_viewer.prev_button.clicked.connect(self.manga_state.prev_chapter)
        self.manga_viewer.next_button.clicked.connect(self.manga_state.next_chapter)
        
        self.root_layout.insertWidget(0, self.manga_dashboard)
        self.root_layout.insertWidget(1, self.manga_viewer)


        self.manager.create_manga("Boundless Necromancer", sites=["AsuraScans"])
        # self.manager.create_manga("Nano Machine", sites=["AsuraScans"])
        # self.manager.create_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!")
        # self.manager.create_manga("Dragon-Devouring Mage")
        
        for manga in self.manager.get_all_manga().values():
            manga.add_chapter(self.manager.get_chapter(manga, 1))
            manga.add_chapter(self.manager.get_chapter(manga, manga.last_chapter))
            mc = self.manga_dashboard.add_manga(manga)
            mc.chapter_clicked.connect(lambda n, manga=manga: self.manga_state.set_manga(manga, n))
        
    def show_manga(self):
        self.manga_viewer.clear()
        
        chapter = self.manager.get_chapter(self.manga_state._manga, self.manga_state.chapter)
        self.manga_state._manga.add_chapter(chapter)
        placeholders, worker = self.manager.get_chapter_images(self.manga_state._manga, chapter, manga_dex=True)
        
        self.manga_viewer.prev_button.setEnabled(not self.manga_state.is_first())
        self.manga_viewer.next_button.setEnabled(not self.manga_state.is_last())
    
        current_y = 0
        for width, height in placeholders:
            self.manga_viewer.add_placeholder(width, height, current_y)
            current_y += height + self.manga_viewer._vertical_spacing
        
        worker.signals.item_completed.connect(lambda r: self.manga_viewer.replace_placeholder(r[0], r[1].content))
        self.manga_state.set_worker(worker)
        
        self.root_layout.setCurrentIndex(1)

    def open_settings(self):
        self.settings_is_opened ^= 1
        if self.settings_is_opened:
            self.settings_window.show()
        else:
            self.settings_window.hide()

    def add_manga(self):
        self.add_manga_window.show()

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
        self.manager.save()
        return super().closeEvent(event)
    
    