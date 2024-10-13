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
from services.scrapers import MangaSiteScraper
from models import Manga




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set up the main window
        self.setWindowTitle("Manga Manager")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(1200, 800)
        # self.setWindowIcon(PySide6.QtGui.QIcon("mangamanager/resources/mangamanager.png"))

        # set up multi window
        self.settings_window = SettingsWindow()
        self.add_manga_window = AddMangaWindow()
        
        self.settings_is_opened = False

        self.scraper = MangaSiteScraper(Manga("Boundless Necromancer", "boundless-necromancer", "data/manga/boundless-necromancer/cover.jpg", ["AsuraScans"], []))
        img = self.scraper.get_chapter_image_iter(1)
        img = QImage().fromData(img)
        img = img.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation)

        # TAB 0
        # add manga
        add_manga_button = QPushButton("Add Manga")
        add_manga_button.setFixedWidth(100)
        add_manga_button.clicked.connect(self.add_manga)

        book_svg_icon = SvgIcon("mangamanager/resources/icons/book-outline.svg")
        lb = QLabel()
        bt = QPushButton()
        bt.setIcon(QIcon(QPixmap("mangamanager/resources/icons/book-outline.svg")))
        lb.setPixmap(book_svg_icon.get_pixmap('grey', 64, 64))
        lb.setAlignment(Qt.AlignCenter)
        lb.setFixedSize(64, 64)
        lb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # manga page
        manga_page_layout = QVBoxLayout()
        manga_page_layout.setAlignment(Qt.AlignCenter)
        manga_page_layout.addWidget(lb)
        manga_page_layout.addWidget(bt)
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
        add_svg_icon = SvgIcon("mangamanager/resources/icons/add-outline.svg")
        airplane_svg_icon = SvgIcon("mangamanager/resources/icons/airplane-outline.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(0), book_svg_icon, "Manga", is_default=True)
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(1), map_svg_icon, "Map")
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(1), add_svg_icon, "Add")
        self.side_menu.add_button(lambda: root_layout.setCurrentIndex(1), airplane_svg_icon, "Airplane")

        self.side_menu.set_settings_function(self.open_settings)


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
    