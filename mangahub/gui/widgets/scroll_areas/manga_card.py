from PySide6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout, QHBoxLayout,
    QFrame, 
    QWidget, QTextEdit
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

from .line_label import LineLabel
from gui.widgets import ImageWidget
from gui.widgets.buttons import ChapterButton, ActionButton
from models.manga import Manga
from directories import *


class MangaCard(QFrame):
    chapter_clicked = Signal(str, float)
    
    def __init__(self, manga: Manga=None, width=295, height=550, parent=None):
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
        
        self.manga: Manga = manga
        
        self.image = ImageWidget(save_original=False)
        self.image.set_clickable()
        self.image.fit(width-20, height-20-150)
        
        self.name_label = LineLabel()
        self.name_label.set_font(QFont("Georgia", 20, 5))
        
        self.last_chapter_button   = self.add_chapter_button()
        self.current_chapter_button = self.add_chapter_button()
        self.first_chapter_button  = self.add_chapter_button()
        
        self.root_layout = QVBoxLayout(self)
        self.root_layout.addWidget(self.image)
        self.root_layout.addWidget(self.name_label)
        self.root_layout.addWidget(self.last_chapter_button)
        self.root_layout.addWidget(self.current_chapter_button)
        self.root_layout.addWidget(self.first_chapter_button)
        
        self.setLayout(self.root_layout)
        
        if manga:
            self.set_manga(manga)
        
    def set_manga(self, manga: Manga) -> 'MangaCard':
        self.manga = manga
        self.image.set_image(f"{self.manga.folder}/{self.manga.cover}")
        self.name_label.setText(self.manga.name)

        last_chapter = manga._chapters_data.get(manga.last_chapter, manga._chapters_data[1])
        current_chapter = manga._chapters_data.get(manga.last_chapter, manga._chapters_data[1])
        
        self.last_chapter_button.set_chapter(last_chapter)
        self.current_chapter_button.set_chapter(current_chapter)
        self.first_chapter_button.set_chapter(manga._chapters_data[1])
        
        return self
        
    def add_chapter_button(self) -> ChapterButton:
        return ChapterButton().add_language()
    
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