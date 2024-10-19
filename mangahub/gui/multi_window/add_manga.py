from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout, QFormLayout,
    QWidget, QPushButton, QLabel, QLineEdit, QComboBox
)


class AddMangaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Manga")

        # manga name
        name_label = QLabel("Name:")

        name_input = QLineEdit()

        # sites manga can be found on
        sites_label = QLabel("Site name:")

        sites_list = QComboBox()
        sites_list.addItem("AsuraScans")

        sites_add_button = QPushButton("Add site")

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