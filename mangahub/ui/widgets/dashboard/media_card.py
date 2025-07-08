from PySide6.QtGui import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout
from loguru import logger

from ..buttons import ChapterButton
from ..image import ImageWidget
from ..scroll_areas import LineLabel

from models.abstract import AbstractMedia
from config import CM


class MediaCard(QFrame):
    chapter_clicked = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setObjectName("MediaCard")
        self.setStyleSheet(f"""#MediaCard {{
            background-color: {CM().widget_bg.name()}; 
            border-radius: 10px;
            border: 1px solid {CM().widget_border.name()};
            }}""")

        self.cover = ImageWidget()
        self.cover.set_placeholder(width=256, height=384)

        self.name_label = LineLabel()
        self.name_label.setFixedWidth(256)
        self.name_label.set_font(font_name="Arial", font_size=18, font_weight=75)

        self.top_button = ChapterButton().add_eye()
        self.mid_button = ChapterButton().add_eye()
        self.bot_button = ChapterButton().add_eye()

        self.root = QVBoxLayout()
        self.root.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root.addWidget(self.cover)
        self.root.addWidget(self.name_label)
        self.root.addWidget(self.top_button)
        self.root.addWidget(self.mid_button)
        self.root.addWidget(self.bot_button)

        self.setLayout(self.root)

        self.name = ""
        self.media: AbstractMedia = None
        self.is_buttons_connected: list[bool] = [False, False, False]

    def set_cover(self, img: ImageWidget.ImageType):
        self.cover.set_image(img)
        return self

    def set_name(self, name: str):
        self.name_label.set_text(name)
        self.name = name
        return self

    def set_date(self, date: str):
        pass

    def _connect_buttons(self):
        if not all(self.is_buttons_connected):
            if self.top_button.chapter and not self.is_buttons_connected[0]:    # If chapter exists and this button is not connected yet
                self.top_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.id_, self.top_button.chapter.num
                    )
                )
                self.is_buttons_connected[0] = True
                
            if self.mid_button.chapter and not self.is_buttons_connected[1]:
                self.mid_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.id_, self.mid_button.chapter.num
                    )
                )
                self.is_buttons_connected[1] = True
                
            if self.bot_button.chapter and not self.is_buttons_connected[2]:
                self.bot_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.id_, self.bot_button.chapter.num
                    )
                )
                self.is_buttons_connected[2] = True
                
        return self

    def set_media(self, media: AbstractMedia):
        self.media = media
        self.set_name(media.id_)
        if media.cover:
            self.set_cover(media.folder / 'cover.webp')
            
        self.set_chapter_nums()
        return self
    
    def set_chapter_nums(self):
        if chap_1 := self.media._chapters_repo.get_i(0):
            self.top_button.set_chapter(chap_1)
        else:
            logger.warning(f'No first chapter in {self.media}')
            
        if chap_cur := self.media.get_chapter(self.media.current_chapter):
            self.mid_button.set_chapter(chap_cur)
        else:
            logger.warning(f'No current chapter in {self.media}')
            
        if chap_last := self.media._chapters_repo.get_i(-1):
            self.bot_button.set_chapter(chap_last)
        else:
            logger.warning(f'No last chapter in {self.media}')
            
        self._connect_buttons()
