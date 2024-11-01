from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout, QHBoxLayout,
    QFrame, 
    QWidget, QPushButton, QLabel
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal

from .smooth_scroll_area import SmoothScrollArea
from ..image import ImageWidget
from models import Manga
from glm import vec2
from directories import *


class MangaCard(QFrame):
    chapter_clicked = Signal(int)
    
    def __init__(self, manga_name, image, parent=None):
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
        
        manga_name_label = QLabel(manga_name)
        manga_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manga_name_label.setFont(QFont("Georgia", 15, 5))
        
        manga_name_scroll = SmoothScrollArea(False)
        manga_name_scroll.scroll_duration = 100
        manga_name_scroll.step_size = 15
        manga_name_scroll.setContentsMargins(0, 0, 0, 0)
        manga_name_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        manga_name_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        manga_name_scroll.setFixedWidth(250)
        manga_name_scroll.setWidget(manga_name_label)
        manga_name_scroll.setWidgetResizable(True)
        
        self.root_layout = QVBoxLayout(self)
        self.root_layout.addWidget(self.image)
        self.root_layout.addWidget(manga_name_scroll)
        
        self.setLayout(self.root_layout)
        
        self.chapter_buttons = {}
        
    def add_chapter_button(self, num, name, upload_date, type='last'):
        name_label = QLabel(f"Chapter {num}{': ' if name else ''}{name if name else ''}")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        date_label = QLabel(f"{upload_date.split('T')[0] if upload_date else ''}")
        date_label.setFont(QFont("Times", 8, 5))
        date_label.setStyleSheet("color: gray;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        vb = QHBoxLayout()
        vb.setContentsMargins(10, 0, 5, 0)
        vb.addWidget(name_label)
        vb.addWidget(date_label)
        
        chapter_button = QPushButton()
        chapter_button.setLayout(vb)
        chapter_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        chapter_button.clicked.connect(lambda _: self.chapter_clicked.emit(num))
        
        self.chapter_buttons[type] = chapter_button
        self.root_layout.addWidget(chapter_button)
        
        return chapter_button
    

class MangaDashboard(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root_layout.setSpacing(20)
        self.root_layout.setContentsMargins(40, 40, 40, 40)
        
        self.root_widget = QWidget()
        self.root_widget.setLayout(self.root_layout)
        
        self.setWidget(self.root_widget)
        
    def add_manga(self, manga: Manga):
        mc = MangaCard(manga.name, manga.cover)
        
        if manga.last_chapter is not None:
            mc.add_chapter_button(manga.last_chapter, manga.chapters[str(manga.last_chapter)].name, manga.chapters[str(manga.last_chapter)].upload_date, 'last')
            
        if manga.current_chapter is not None:
            mc.add_chapter_button(manga.current_chapter, manga.chapters[manga.current_chapter].name, manga.chapters[manga.current_chapter].upload_date, 'current')
            
        mc.add_chapter_button(1, manga.chapters["1"].name, manga.chapters["1"].upload_date, 'first')
        
        self.root_layout.addWidget(mc)
        return mc
        