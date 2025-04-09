from typing import TYPE_CHECKING

from directories import ICONS_DIR
from ui.widgets import SvgIcon
from models import URL
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QComboBox, QFormLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QVBoxLayout, QWidget)
from services.parsers import UrlParser

if TYPE_CHECKING:
    from controllers import AppController


class AddMangaWindow(QMainWindow):
    def __init__(self, app_controller: 'AppController', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Manga")
        self.setFixedWidth(300)
        
        self.manager = app_controller.manga_manager
        self.sites_manager = app_controller.sites_manager

        # manga name
        name_label = QLabel("Name:")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Manga name or URL")

        # manga url
        url_label = QLabel("URL:")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        self.url_input.textChanged.connect(self.url_handler)

        # sites manga can be found on
        sites_label = QLabel("Site name:")

        main_site_list = QComboBox()
        main_site_list.addItems(list(self.sites_manager.get_all_sites().keys()))
        
        sites_list = QComboBox()

        sites_add_button = QPushButton()
        sites_add_button.setStyleSheet("QPushButton { background-color: transparent; border: 2px dashed grey; border-radius: 5px; }")
        sites_add_button.setIcon(SvgIcon(ICONS_DIR / "add.svg").get_icon('white'))
        sites_add_button.setIconSize(QSize(16, 16))

        sites_layout = QVBoxLayout()
        sites_layout.addWidget(main_site_list)
        sites_layout.addWidget(sites_add_button)

        self.add_manga_button = QPushButton("Add Manga")
        self.add_manga_button.clicked.connect(lambda: self.manager.create_manga(self.name_input.text(), site=main_site_list.currentText()))
        
        # root layout
        root_layout = QFormLayout()
        root_layout.addRow(name_label, self.name_input)
        root_layout.addRow(url_label, self.url_input)
        root_layout.addRow(sites_label, sites_layout)
        root_layout.addWidget(self.add_manga_button)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)
        
    def url_handler(self, text):
        if URL.is_url(text):
            url = URL(url=text)
            if not self.name_input.text():
                self.name_input.setText(UrlParser(url).manga_name)
        