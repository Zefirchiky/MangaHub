from PySide6.QtGui import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

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
            if self.top_button.chapter and not self.is_buttons_connected[0]:    # If chapter and this button is not connected yet
                self.top_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.name, self.top_button.chapter.num
                    )
                )
                self.is_buttons_connected[0] = True
                
            if self.mid_button.chapter and not self.is_buttons_connected[1]:
                self.mid_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.name, self.mid_button.chapter.num
                    )
                )
                self.is_buttons_connected[1] = True
                
            if self.bot_button.chapter and not self.is_buttons_connected[2]:
                self.bot_button.clicked.connect(
                    lambda: self.chapter_clicked.emit(
                        self.media.name, self.bot_button.chapter.num
                    )
                )
                self.is_buttons_connected[2] = True
                
        return self

    def set_media(self, media: AbstractMedia):
        self.media = media
        self.set_name(media.name)
        if media.cover:
            self.set_cover(media.folder / media.cover)
            
        self.update_buttons()
        self._connect_buttons()
        return self

    def update_buttons(self):
        if chap := self.media.get_chapter(self.media.first_chapter):
            self.top_button.set_chapter(chap)
        if chap := self.media.get_chapter(self.media.current_chapter):
            self.mid_button.set_chapter(chap)
        if self.media.last_chapter != -1 and (chap := self.media.get_chapter(self.media.last_chapter)):
            self.bot_button.set_chapter(chap)
