from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout, QHBoxLayout,
    QFrame, 
    QWidget, QPushButton, QLabel
)
from PySide6.QtGui import QPixmap, QIcon, QPalette, QFont
from PySide6.QtCore import Qt, Signal

from .smooth_scroll_area import SmoothScrollArea
from ..image import ImageWidget
from models import Manga
from glm import vec2
from directories import *


class MangaCard(QFrame):
    chapter_clicked = Signal(int)
    
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setObjectName("manga_card")
        self.setStyleSheet(f'''
            #manga_card {{
                background-color: {self.palette().window().color().name()};
                border-radius: 15px;
                border: 1px solid {self.palette().window().color().darker().name()};
                color: black;
            }}
            ''')
        self.setAutoFillBackground(True)
        
        self.image = ImageWidget(image)
        self.image.scale_to_width(25)
        self.image.scale_to_width(250)
        self.image.fit(vec2(250, 300))
        self.image.signals.clicked_l.connect(lambda: print("clicked"))
        
        manga_name_label = QLabel("Nano Machine")
        manga_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manga_name_label.setFont(QFont("Times", 24, 5))
        
        self.root_layout = QVBoxLayout(self)
        self.root_layout.addWidget(self.image)
        self.root_layout.addWidget(manga_name_label)
        
        self.setLayout(self.root_layout)
        
        self.chapter_buttons = {}
        
    def add_chapter_button(self, num, name, upload_date, type='last'):
        name_label = QLabel(f"Chapter {num}{': ' if name else ''}{name if name else ''}")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        date_label = QLabel(f"{upload_date.split('T')[0]}")
        date_label.setFont(QFont("Times", 8, 5))
        date_label.setStyleSheet("color: gray;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        vb = QHBoxLayout()
        vb.setContentsMargins(10, 0, 5, 0)
        vb.addWidget(name_label)
        vb.addWidget(date_label)
        
        chapter_button = QPushButton()
        chapter_button.setLayout(vb)
        chapter_button.clicked.connect(lambda _: self.chapter_clicked.emit(num))
        
        self.chapter_buttons[type] = chapter_button
        self.root_layout.addWidget(chapter_button)
        
        return chapter_button
    

class MangaDashboard(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        mc = MangaCard(f"{MANGA_DIR}/nano-machine/cover.jpg")
        mc.add_chapter_button(270, "Last chapter", "2022-01-01").clicked.connect(lambda: print("Last chapter"))
        mc.add_chapter_button(138, "Current chapter", "2022-01-01").clicked.connect(lambda: print("Current chapter"))
        mc.add_chapter_button(1, "First chapter", "2022-01-01").clicked.connect(lambda: print("First chapter"))
        
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root_layout.setSpacing(20)
        self.root_layout.setContentsMargins(40, 40, 40, 40)
        self.root_layout.addWidget(mc)
        
        self.root_widget = QWidget()
        self.root_widget.setLayout(self.root_layout)
        
        self.setWidget(self.root_widget)
        
    def add_manga(self, manga: Manga):
        mc = MangaCard(manga.cover)
        
        if manga.last_chapter is not None:
            mc.add_chapter_button(manga.last_chapter, manga.chapters[str(manga.last_chapter)].name, manga.chapters[str(manga.last_chapter)].upload_date, 'last')
            
        if manga.current_chapter is not None:
            mc.add_chapter_button(manga.current_chapter, manga.chapters[manga.current_chapter].name, manga.chapters[manga.current_chapter].upload_date, 'current')
            
        mc.add_chapter_button(1, manga.chapters["1"].name, manga.chapters["1"].upload_date, 'first')
        
        self.root_layout.addWidget(mc)
        return mc
        