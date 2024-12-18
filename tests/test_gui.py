from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap
from image import ImageWidget


class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 900)
        ImageWidget.set_default_placeholder('mangahub/resources/img/placeholder.jpg', width=200, height=300)
        # ImageWidget.set_default_error_image(QPixmap(300, 200))
        
        self.image = ImageWidget()
        self.image.set_placeholder(width=400, height=200)
        
        self.root_layout = QVBoxLayout()
        self.root_layout.addWidget(self.image)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.root_layout)
                
    def run(self):
        self.show()

app = QApplication([])
test = Test()
test.run()
app.exec()