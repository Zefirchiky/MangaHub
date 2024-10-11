from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QVBoxLayout, QHBoxLayout, QStackedLayout,
    QSizePolicy,
    QWidget, QToolBar, QPushButton, QLabel, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QAction, QPixmap, QImage, QCursor, QIcon
from PySide6.QtSvgWidgets import QSvgWidget

from .multi_window.add_manga import AddMangaWindow
from .multi_window.settings import SettingsWindow
from .widgets.side_menu import SideMenu
from .widgets.svg import SvgIcon
from scrapers import MangaTitlePageScraper




class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        # set up the main window
        self.setWindowTitle("Manga Manager")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(1200, 800)
        # self.setWindowIcon(PySide6.QtGui.QIcon("mangamanager/resources/mangamanager.png"))

        # set up multi window
        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow()
        
        self.settings_is_opened = False

        self.scraper = MangaTitlePageScraper("https://asuracomic.net/series/nano-machine-b6b7f63d/chapter/228")
        img = self.scraper.get_chapter_page()
        img = QImage().fromData(img)
        img = img.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation)
        img.save("mangamanager/data/manga/boundless_necromancer/chapters/chapter1-name/1_1_scaled.webp")

        # TAB 0
        # add manga
        add_manga_button = QPushButton("Add Manga")
        add_manga_button.setFixedWidth(100)
        add_manga_button.clicked.connect(self.add_manga)

        # manga page
        manga_page_layout = QVBoxLayout()
        manga_page_layout.setAlignment(Qt.AlignCenter)
        manga_page_layout.addWidget(QLabel("Manga Manager"))
        manga_page_layout.addWidget(add_manga_button)

        manga_page_widget = QWidget()
        manga_page_widget.setLayout(manga_page_layout)

        # TAB 1
        # set up manga reader
        img_label = QLabel()
        img_label.setPixmap(QPixmap(img))
        img_label.setAlignment(Qt.AlignCenter)

        scrollable_label = QScrollArea()
        scrollable_label.setAlignment(Qt.AlignCenter)
        scrollable_label.setWidgetResizable(True)
        scrollable_label.setWidget(img_label)

        # manga reader
        manga_reader_layout = QVBoxLayout()
        manga_reader_layout.setAlignment(Qt.AlignCenter)
        manga_reader_layout.addWidget(scrollable_label)

        manga_reader_widget = QWidget()
        manga_reader_widget.setLayout(manga_reader_layout)

        # root layout
        root_layout = QStackedLayout()
        root_layout.insertWidget(0, manga_page_widget)
        root_layout.insertWidget(1, manga_reader_widget)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)

        # side menu
        book_svg_icon = SvgIcon("mangamanager/resources/icons/book-outline.svg")
        map_svg_icon = SvgIcon("mangamanager/resources/icons/map-outline.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(0), book_svg_icon, "Manga", is_default=True)
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(1), map_svg_icon, "Map")

        self.side_menu.settings_button.clicked.connect(self.open_settings)

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)

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
            self.side_menu.show_menu()
        elif self.side_menu._width + 40 < cursor_pos.x() - window_pos.x() <= self.side_menu._width + 340:
            self.side_menu.show_half_menu()
        else:
            self.side_menu.hide_menu()

    def resizeEvent(self, event):
        self.side_menu.adjust_geometry()

        return super().resizeEvent(event)


class MainGui:
    def __init__(self, app):
        self.app = app
        self.qt_app = QApplication()
        self.main_window = MainWindow(app)

    def start(self):
        self.main_window.showMaximized()
        self.qt_app.exec()