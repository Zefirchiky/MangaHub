from __future__ import annotations
from typing import TYPE_CHECKING

from ui.widgets import IconRepo
from models import Url
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from services.parsers import UrlParser
from ui.widgets.buttons import IconButton, IconTypes

if TYPE_CHECKING:
    from controllers import AppController


class AddMangaWindow(QMainWindow):
    def __init__(self, app_controller: AppController, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Manga")
        self.setFixedWidth(600)

        self.manager = app_controller.manga_manager
        self.sites_manager = app_controller.sites_manager

        # manga name
        name_label = QLabel("Name:")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Manga name or URL")

        self.find_button = IconButton(IconTypes.SEARCH, size=24)
        self.find_button.clicked.connect(lambda: self.find_button.setDisabled(True))
        
        self.name_widget = QWidget()
        self.name_layout = QHBoxLayout(self.name_widget)
        self.name_layout.addWidget(self.name_input)
        self.name_layout.addWidget(self.find_button)

        # sites manga can be found on
        self.sites_label = QLabel("Sites name:")

        self.sites_list = QComboBox()

        sites_layout = QVBoxLayout()
        sites_layout.addWidget(self.sites_list)

        self.add_manga_button = QPushButton("Add Manga")
        self.add_manga_button.clicked.connect(lambda: self.hide())

        # root layout
        root_layout = QFormLayout()
        root_layout.addRow(name_label, self.name_widget)
        root_layout.addRow(self.sites_label, sites_layout)
        root_layout.addWidget(self.add_manga_button)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)

    def url_handler(self, text):
        if Url.is_url(text):
            url = Url(url=text)
            if not self.name_input.text():
                self.name_input.setText(UrlParser(url).manga_id)
