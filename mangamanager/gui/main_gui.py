from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QVBoxLayout, 
    QWidget, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Manga Manager")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        # self.setWindowIcon(PySide6.QtGui.QIcon("mangamanager/resources/mangamanager.png"))

        root_layout = QVBoxLayout()
        # root_layout.addWidget()

        root = QWidget()
        root.setLayout(root_layout)


        self.setCentralWidget(root)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)


        manga_action = QAction("Mangas", self)
        tool_bar.addAction(manga_action)

class MainGui:
    def __init__(self, app):
        self.app = app
        self.qt_app = QApplication()
        self.main_window = MainWindow(app)

    def start(self):
        self.main_window.showMaximized()
        self.qt_app.exec()