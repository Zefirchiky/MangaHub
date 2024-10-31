from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout, QStackedLayout, 
    QWidget, QPushButton, QLabel
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QCursor, QIcon

from .multi_window.add_manga import AddMangaWindow
from .multi_window.settings import SettingsWindow
from gui.gui_utils import MM
from .widgets.slide_menus import SideMenu, SlideMenu
from .widgets.svg import SvgIcon
from .widgets.scroll_areas import MangaViewer, MangaDashboard
from controllers import MangaManager
from models import MangaChapter
from directories import *


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("MangaHub")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("resources/app_icon.ico"))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow()
        
        self.settings_is_opened = False


        # TAB 0
        # Create manga button for Nano Machine
        nano_layout = QVBoxLayout()
        nano_cover = QLabel()
        nano_cover.setPixmap(QPixmap(f"{MANGA_DIR}/nano-machine/cover.jpg").scaledToWidth(400, Qt.TransformationMode.SmoothTransformation))
        nano_layout.addWidget(nano_cover)
        
        self.nano_button = QPushButton("Nano Machine") 
        self.nano_button.setFixedSize(400, 700)
        self.nano_button.setLayout(nano_layout)
        self.nano_button.clicked.connect(lambda: self.show_manga('Nano Machine', 230))
        self.nano_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Create manga button for Boundless Necromancer
        self.boundless_button = QPushButton("Boundless Necromancer")
        self.boundless_button.clicked.connect(lambda: self.show_manga('Boundless Necromancer', 1))
        
        # add manga
        self.add_manga_button = QPushButton("Add Manga")
        self.add_manga_button.setFixedWidth(100)
        self.add_manga_button.clicked.connect(self.add_manga)
        
        book_svg_icon = SvgIcon(f"{ICONS_DIR}/book-outline.svg")
        lb = QLabel()
        bt = QPushButton()
        bt.setIcon(QIcon(QPixmap(f"{ICONS_DIR}/book-outline.svg")))
        lb.setPixmap(book_svg_icon.get_pixmap('grey', 64, 64))
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb.setFixedSize(64, 64)
        lb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # manga page
        manga_page_layout = QVBoxLayout()
        manga_page_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manga_page_layout.addWidget(lb)
        manga_page_layout.addWidget(bt)
        manga_page_layout.addWidget(QLabel("Manga Manager"))
        manga_page_layout.addWidget(self.nano_button)
        manga_page_layout.addWidget(self.boundless_button)
        manga_page_layout.addWidget(self.add_manga_button)

        manga_page_widget = QWidget()
        manga_page_widget.setLayout(manga_page_layout)

        # TAB 1
        self.manga_viewer = MangaViewer()

        # manga reader
        # manga_reader_layout = QVBoxLayout()
        # manga_reader_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # manga_reader_layout.addWidget(self.manga_viewer)

        # manga_reader_widget = QWidget()
        # manga_reader_widget.setLayout(manga_reader_layout)
        
        # TAB 3
        # manga dashboard
        self.manga_dashboard = MangaDashboard()

        # root layout
        self.root_layout = QStackedLayout()
        self.root_layout.insertWidget(0, manga_page_widget)
        self.root_layout.insertWidget(1, self.manga_viewer)
        self.root_layout.insertWidget(2, self.manga_dashboard)
        root = QWidget()
        root.setLayout(self.root_layout)

        self.setCentralWidget(root)


        # side menu
        book_svg_icon = SvgIcon(f"{ICONS_DIR}/book-outline.svg")
        map_svg_icon = SvgIcon(f"{ICONS_DIR}/map-outline.svg")
        add_svg_icon = SvgIcon(f"{ICONS_DIR}/add-outline.svg")
        airplane_svg_icon = SvgIcon(f"{ICONS_DIR}/airplane-outline.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(0), book_svg_icon, "Manga", is_default=True)
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(1), map_svg_icon, "Map")
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(2), add_svg_icon, "Add")
        self.side_menu.add_button(lambda: self.root_layout.setCurrentIndex(1), airplane_svg_icon, "Airplane")

        self.side_menu.set_settings_function(self.open_settings)

        self.slide_menu = SlideMenu(self)
        self.slide_menu.adjust_geometry_with_animation(self.slide_menu.get_geometry(1700, 0, 72, 0), self.slide_menu.get_geometry(1700, 0, 100, 0))


        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)
        
    def init(self):
        self.manager: MangaManager = self.app.manga_manager
        # manga = self.manager.create_manga("Boundless Necromancer")
        # manga_ = self.manager.create_manga("Nano Machine")
        # manga__ = self.manager.create_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!")
        bn = self.manga_dashboard.add_manga(self.manager.get_manga("Boundless Necromancer"))
        bn.chapter_clicked.connect(lambda n: self.show_manga("Boundless Necromancer", n))
        it = self.manga_dashboard.add_manga(self.manager.get_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!"))
        it.chapter_clicked.connect(lambda n: self.show_manga("I, The Demon Lord, Am Being Targeted by My Female Disciples!", n))
        nm = self.manga_dashboard.add_manga(self.manager.get_manga("Nano Machine"))
        nm.chapter_clicked.connect(lambda n: self.show_manga("Nano Machine", n))
        
    def show_manga(self, manga_title, num):
        self.root_layout.removeWidget(self.manga_viewer)
        self.manga_viewer = MangaViewer()
        self.root_layout.insertWidget(1, self.manga_viewer)
        
        manga = self.manager.get_manga(manga_title)
        chapter = self.manager.get_chapter(manga, num)
        placeholders, worker = self.manager.get_chapter_images(chapter, manga_title, manga_dex=True)
    
        # Create placeholders at each y-level based on sizes
        current_y = 0
        for width, height in placeholders:
            self.manga_viewer.add_placeholder(width, height, current_y)
            current_y += height + self.manga_viewer._vertical_spacing
        
        # Display each image as it downloads, replacing placeholders
        worker.signals.item_completed.connect(lambda r: self.manga_viewer.replace_placeholder(r[0], r[1].content))

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
        if 0 <= cursor_pos.x() - window_pos.x() <= self.side_menu._width - 40:
            self.side_menu.show_menu()
        elif self.side_menu._width + 40 < cursor_pos.x() - window_pos.x() <= self.side_menu._width + 400:
            self.side_menu.show_half_menu()
        else:
            self.side_menu.hide_menu()

    def resizeEvent(self, event):
        self.side_menu.adjust_geometry()
        MM().pos_update()

        return super().resizeEvent(event)
    
    