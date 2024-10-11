from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QVBoxLayout, QHBoxLayout, 
    QSizePolicy,
    QWidget, QToolBar, QPushButton, QLabel, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QAction, QPixmap, QImage, QCursor, QIcon
from PySide6.QtSvgWidgets import QSvgWidget

from .multi_window.add_manga import AddMangaWindow
from .widgets.side_menu import SideMenu
from .widgets.svg import SvgIcon
from scrapers import MangaTitlePageScraper




class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Manga Manager")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(1200, 800)
        # self.setWindowIcon(PySide6.QtGui.QIcon("mangamanager/resources/mangamanager.png"))

        self.scraper = MangaTitlePageScraper("https://asuracomic.net/series/nano-machine-b6b7f63d/chapter/228")
        img = self.scraper.get_chapter_page()
        img = QImage().fromData(img)
        # img.invertPixels(QImage.InvertMode.InvertRgb)
        # img = img.scaled(480, 480, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        img = img.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation)
        img.save("mangamanager/data/manga/boundless_necromancer/chapters/chapter1-name/1_1_scaled.webp")
        print(img.deviceIndependentSize())
        # img = img.createHeuristicMask() # only saves white (???)
        # img = img.transformed(Qt.KeepAspectRatio, 480)
        # img = QPixmap(img)

        
        img_label = QLabel()
        img_label.setPixmap(QPixmap(img))
        img_label.setAlignment(Qt.AlignCenter)
        print(img.width())
        # img_label.setSizePolicy(QSizePolicy.setHeightForWidth())

        scrollable_label = QScrollArea()
        scrollable_label.set
        scrollable_label.setFixedWidth(img.width() + 15)
        scrollable_label.setWidgetResizable(True)
        scrollable_label.setAlignment(Qt.AlignCenter)
        scrollable_label.setWidget(img_label)

        add_manga_button = QPushButton("Add Manga")
        add_manga_button.setFixedWidth(100)
        add_manga_button.clicked.connect(self.add_manga)

        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(QLabel("Manga Manager"))
        root_layout.addWidget(add_manga_button)
        root_layout.addWidget(scrollable_label)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)

        # side menu
        book_svg_icon = SvgIcon("mangamanager/resources/icons/book-outline.svg")
        map_svg_icon = SvgIcon("mangamanager/resources/icons/map-outline.svg")

        self.side_menu = SideMenu(self)
        self.side_menu.add_button(book_svg_icon, "Manga")
        self.side_menu.add_button(map_svg_icon, "Map")

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)

    def add_manga(self):
        self.window = AddMangaWindow()
        
        self.window.show()

    def check_mouse_position(self):
        cursor_pos = QCursor.pos()
        window_pos = self.mapToGlobal(QPoint(0, 0))
        if 0 <= cursor_pos.x() - window_pos.x() <= self.side_menu._width + 40:
            self.side_menu.show_menu()
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