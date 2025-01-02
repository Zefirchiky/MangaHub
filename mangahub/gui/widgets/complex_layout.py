from PySide6.QtWidgets import QStackedLayout, QHBoxLayout


class ComplexLayout(QStackedLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def add_HLayout(self, name=None):
        layout = QHBoxLayout()
        self.addLayout(layout)
        return layout