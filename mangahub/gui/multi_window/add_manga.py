from PySide6.QtWidgets import (
    QMainWindow,
    QHBoxLayout, QVBoxLayout, QFormLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QSize
from gui.widgets import SvgIcon
from directories import ICONS_DIR


class AddMangaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Manga")
        self.setFixedWidth(300)

        # manga name
        name_label = QLabel("Name:")

        name_input = QLineEdit()
        name_input.setPlaceholderText("Manga name or URL")

        # sites manga can be found on
        sites_label = QLabel("Site name:")

        chosen_sites_list = QHBoxLayout()
        
        sites_list = QComboBox()

        sites_add_button = QPushButton()
        sites_add_button.setStyleSheet("QPushButton { background-color: transparent; border: 2px dashed grey; border-radius: 5px; }")
        sites_add_button.setIcon(SvgIcon(f"{ICONS_DIR}/plus.svg").get_icon('white'))
        sites_add_button.setIconSize(QSize(16, 16))

        sites_layout = QVBoxLayout()
        sites_layout.addWidget(sites_list)
        sites_layout.addWidget(sites_add_button)

        button = QPushButton("Add Manga")
        
        # root layout
        root_layout = QFormLayout()
        root_layout.addRow(name_label, name_input)
        root_layout.addRow(sites_label, sites_layout)
        root_layout.addWidget(button)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)