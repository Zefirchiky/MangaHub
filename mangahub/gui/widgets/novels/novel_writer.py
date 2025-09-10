from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout

from .novel_text_edit import NovelTextEdit


class NovelWriter(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.font_ = QFont('New Times Roman', 12)
        
        self.text_edit = NovelTextEdit()
        self.text_edit.setFont(self.font_)
        
        self.root_layout = QVBoxLayout()
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.root_layout.addWidget(self.text_edit)
        self.setLayout(self.root_layout)
        
        self.setContentsMargins(30, 30, 30, 30)
        
        