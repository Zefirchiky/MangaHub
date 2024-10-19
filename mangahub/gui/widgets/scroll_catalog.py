from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout, QVBoxLayout,
    QScrollArea
    )


class ScrollCatalog(QScrollArea):
    def __init__(self):
        super().__init__()

        self.catalog_layout = QVBoxLayout()
        self.catalog_layout.setStretch(0, 1)

        self.catalog_widget = QWidget()
        self.catalog_widget.setLayout(self.catalog_layout)

        self.catalog = QScrollArea(self.catalog_widget)

        root_layout = QHBoxLayout()
        root_layout.addLayout(self.catalog_layout)

        self.setLayout(root_layout)