from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt
from .smooth_scroll_area import SmoothScrollArea
from models.novels import Novel
from directories import BACKGROUNDS_DIR


class NovelViewer(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.viewport().setObjectName("NovelViewer")
        self.viewport().setStyleSheet(f"""
                            #NovelViewer {{
                                background: url({str(BACKGROUNDS_DIR).replace('\\', '/')}/novel_viewer.jpg) repeat;
                            }}
                           """)
        
        
        self.text = QTextBrowser()
        self.text.setFixedWidth(1000)
        
        self.setWidget(self.text)
        
        self.novel: Novel = None
        
    def set_novel(self, novel: Novel):
        self.text.setHtml(novel.text)