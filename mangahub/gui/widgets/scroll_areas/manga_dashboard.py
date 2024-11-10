from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout, QHBoxLayout,
    QFrame, 
    QWidget, QPushButton, QLabel
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, Signal
from glm import vec2

from .smooth_scroll_area import SmoothScrollArea
from ..image import ImageWidget
from models import Manga
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
        
    def add_chapter_button(self, num, name, upload_date, type='last', insertion=0):
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
        
        self.chapter_buttons[type] = [chapter_button, name_label, date_label]
        if not insertion:
            self.root_layout.addWidget(chapter_button)
        else:
            self.root_layout.insertWidget(insertion, chapter_button)
        
        return chapter_button
        

class MangaDashboard(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.add_manga_button = QPushButton("Add Manga", parent=self)
        self.add_manga_button.setFixedSize(100, 32)
        self.add_manga_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_manga_button.move(self.width() - self.add_manga_button.width() - 15, 10)
        
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root_layout.setSpacing(20)
        self.root_layout.setContentsMargins(40, 40, 40, 40)
        
        self.root_widget = QWidget()
        self.root_widget.setLayout(self.root_layout)
        
        self.setWidget(self.root_widget)
        
        self.manga = {}
        
    def add_manga(self, manga: Manga):
        mc = MangaCard(manga.name, f"{manga.folder}/{manga.cover}")
        
        if manga.last_chapter:
            mc.add_chapter_button(manga.last_chapter, manga._chapters_data[manga.last_chapter].name, manga._chapters_data[manga.last_chapter].upload_date, 'last')
            
        if manga.current_chapter and manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter:
            mc.add_chapter_button(manga.current_chapter, manga._chapters_data[manga.current_chapter].name, manga._chapters_data[manga.current_chapter].upload_date, 'current')
            
        mc.add_chapter_button(1, manga._chapters_data[1].name, manga._chapters_data[1].upload_date, 'first')
        
        self.manga[manga.name] = mc
        self.root_layout.addWidget(mc)
        return mc
    
    def update_manga(self, manga: Manga):
        mc: MangaCard = self.manga[manga.name]
        if manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter:
            if mc.chapter_buttons.get('current'):
                mc.chapter_buttons['current'][1].setText(f"Chapter {manga.current_chapter}{': ' if manga._chapters_data[manga.current_chapter].name else ''}{manga._chapters_data[manga.current_chapter].name if manga._chapters_data[manga.current_chapter].name else ''}")
            else:
                mc.add_chapter_button(manga.current_chapter, manga._chapters_data[manga.current_chapter].name, manga._chapters_data[manga.current_chapter].upload_date, 'current', 3)
        
    def resizeEvent(self, arg__1):
        self.add_manga_button.move(self.width() - self.add_manga_button.width() - 15, 10)
        return super().resizeEvent(arg__1)
        