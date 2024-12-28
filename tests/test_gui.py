from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtGui import QPixmap
from image import ImageWidget


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 900)
        path = 'D:/AllArtem/Programmer/WIP/MangaHub/mangahub/resources/background/novel_viewer.jpg'
        
        self.ar = QScrollArea()
        self.ar.viewport().setStyleSheet(f"background: url({path}) repeat;")
        
        self.root_layout = QVBoxLayout()
        self.root_layout.addWidget(self.ar)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.root_layout)
                
    def run(self):
        self.show()


app = QApplication([])
test = Test()
test.run()
app.exec()