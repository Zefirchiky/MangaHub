from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout, QHBoxLayout,
    QFrame, 
    QWidget, QPushButton, QLabel, QTextEdit
)
from PySide6.QtGui import QFont, QCursor
from PySide6.QtCore import Qt, QSize, Signal

from .line_label import LineLabel
from .smooth_scroll_area import SmoothScrollArea
from ..image import ImageWidget
from ..svg import SvgIcon
from ..action_button import ActionButton
from models import Manga
from directories import *


class MangaCard(QFrame):
    chapter_clicked = Signal(str, float)
    
    def __init__(self, manga: Manga, width=295, height=550, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(width, height)
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
        
        self.manga = manga
        
        self.image = ImageWidget(f"{self.manga.folder}/{self.manga.cover}", save_original=False)
        self.image.set_clickable()
        self.image.fit(width-20, height-20-150)
        
        self.name_label = LineLabel(self.manga.name)
        self.name_label.set_font(QFont("Georgia", 20, 5))
        
        self.root_layout = QVBoxLayout(self)
        self.root_layout.addWidget(self.image)
        self.root_layout.addWidget(self.name_label)
        
        self.setLayout(self.root_layout)
        
        self.chapter_buttons = {}
        
    def add_chapter_button(self, num: int | float, name: str, upload_date, type='last', insertion=0):
        name_label = QLabel(f"Chapter {num}{': ' if name else ''}{name if name else ''}")   # 'Chapter 1: Name' or 'Chapter 1'
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
        chapter_button.clicked.connect(lambda _: self.chapter_clicked.emit(self.manga.name, num))
        
        self.chapter_buttons[type] = [chapter_button, name_label, date_label]
        if not insertion:
            self.root_layout.addWidget(chapter_button)
        else:
            self.root_layout.insertWidget(insertion, chapter_button)
        
        return chapter_button
    
    def open_full_card(self):
        full_manga_card = FullMangaCard(self.manga)
        full_manga_card.show()
    
    
class FullMangaCard(QFrame):
    def __init__(self, width=1200, height=800, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setGeometry(self.parent().width()//2 - width//2, self.parent().height()//2 - height//2, width, height)
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
        
        
        # === VARIABLES ===
        self.content_margins = 10
        self.is_edit_mode = False
        
        # Frame widgets
        self.close_button_size = 32
        self.edit_button_size = 32
        
        # Cover
        self.cover_width = 280
        self.cover_height = 400
        
        # Name
        self.name_label_width = 800
        
        
        # === MANGA INFO ===
        self.manga: Manga = None
        
        # Cover
        self.cover = ImageWidget(save_original=False)
        self.cover.set_clickable()
        self.cover.fit(self.cover_width, self.cover_height)
        
        # Name
        self.name_label = LineLabel()
        self.name_label.setFixedWidth(self.name_label_width)
        self.name_label.set_font(QFont("Georgia", 20, 5))
        
        # Description
        self.description_label = QTextEdit()
        self.description_label.setFont(QFont("Times", 15, 5))
        self.description_label.setStyleSheet("background-color: transparent; border: none;")
        self.description_label.textChanged.connect(self.change_manga_description)
                
        # Info layout except cover
        self.manga_info_layout = QVBoxLayout()
        self.manga_info_layout.addSpacing(10)
        self.manga_info_layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.manga_info_layout.addSpacing(20)
        self.manga_info_layout.addWidget(self.description_label)
        self.manga_info_layout.addStretch(1)
        
        # Info layout
        self.manga_layout = QHBoxLayout()
        self.manga_layout.addWidget(self.cover)
        self.manga_layout.addSpacing(20)
        self.manga_layout.addLayout(self.manga_info_layout)

        # === CHAPTERS ===
        self.chapters_layout = QVBoxLayout()
        self.chapters_widget = QWidget()
        self.chapters_widget.setLayout(self.chapters_layout)
        self.chapters_widget.setFixedHeight(400)
        
        # === ROOT LAYOUT ===
        self.root_layout = QVBoxLayout(self)
        self.root_layout.addLayout(self.manga_layout)
        self.root_layout.addWidget(self.chapters_widget)
                
        
        # === FRAME WIDGETS ===
        # Close
        self.close_button = ActionButton(ActionButton.Types.CLOSE, fn=self.close, size=self.close_button_size, parent=self)
        self.close_button.move(self.width() - self.close_button.width() - self.content_margins, self.content_margins)
        
        # Edit
        self.edit_button = ActionButton(ActionButton.Types.EDIT, fn=self.edit_mode, size=self.edit_button_size, parent=self)
        self.edit_button.move(self.width() - self.edit_button.width() - self.content_margins, 
                              self.cover_height - self.edit_button.height() + self.content_margins)
        
        self.setContentsMargins(self.content_margins, self.content_margins, self.content_margins, self.content_margins)
        self.setLayout(self.root_layout)
        
    def edit_mode(self):
        if self.is_edit_mode:
            self.is_edit_mode = False
            self.description_label.setReadOnly(True)
            self.edit_button.setIcon(SvgIcon(ICONS_DIR / "edit.svg").get_icon('white'))
            self.description_label.setStyleSheet("background-color: transparent; border: none;")
        else:
            self.is_edit_mode = True
            self.description_label.setReadOnly(False)
            self.edit_button.setIcon(SvgIcon(ICONS_DIR / "save.svg").get_icon('white'))
            self.description_label.setStyleSheet("")
        
    def set_manga(self, manga: Manga):
        self.manga = manga
        self.cover.set_image(f"{self.manga.folder}/{self.manga.cover}")
        self.name_label.setText(self.manga.name)
        self.description_label.setText(self.manga.description)
        # self.set_chapters(manga)
        
    def change_manga_description(self):
        self.manga.description = self.description_label.toPlainText()
        
    def update_geometry(self):
        self.setGeometry(self.parent().width()//2 - self.width()//2, self.parent().height()//2 - self.height()//2, self.width(), self.height())
        
 
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
        self.root_layout.setContentsMargins(20, 40, 20, 40)
        
        self.fmc = FullMangaCard(parent=self)
        self.fmc.cover.clicked_l.connect(self.fmc.close)
        self.fmc.close()
        
        self.root_widget = QWidget()
        self.root_widget.setLayout(self.root_layout)
        
        self.setWidget(self.root_widget)
        
        self.manga: dict[str, MangaCard] = {}
        
    def add_manga(self, manga: Manga):
        mc = MangaCard(manga)
        mc.image.clicked_l.connect(lambda manga=manga: self.fmc.set_manga(manga))
        mc.image.clicked_l.connect(self.fmc.show)
        
        if manga.last_chapter:
            mc.add_chapter_button(manga.last_chapter, manga._chapters_data[manga.last_chapter].name, manga._chapters_data[manga.last_chapter].upload_date, 'last')
            
        if manga.current_chapter and manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter:
            mc.add_chapter_button(manga.current_chapter, manga._chapters_data[manga.current_chapter].name, manga._chapters_data[manga.current_chapter].upload_date, 'current')
        else:
            mc.add_chapter_button(1, manga._chapters_data[1].name, manga._chapters_data[1].upload_date, 'current')
            
        mc.add_chapter_button(1, manga._chapters_data[1].name, manga._chapters_data[1].upload_date, 'first')
        
        self.manga[manga.name] = mc
        self.root_layout.addWidget(mc)
        return mc        
    
    def update_manga(self, manga: Manga):
        mc: MangaCard = self.manga[manga.name]
        if manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter:
            if mc.chapter_buttons.get('current'):
                mc.chapter_buttons['current'][1].setText(f"Chapter {manga.current_chapter}")
                mc.chapter_buttons['current'][0].clicked.disconnect()
                mc.chapter_buttons['current'][0].clicked.connect(lambda _: mc.chapter_clicked.emit(manga.name, manga.current_chapter))
            else:
                mc.add_chapter_button(manga.current_chapter, manga._chapters_data[manga.current_chapter].name, manga._chapters_data[manga.current_chapter].upload_date, 'current', 3)
        
    def resizeEvent(self, arg__1):
        self.add_manga_button.move(self.width() - self.add_manga_button.width() - 15, 10)
        self.fmc.update_geometry()
        return super().resizeEvent(arg__1)
        