from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QWidget, QPushButton
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

from gui.widgets.separators import Separator
from .smooth_scroll_area import SmoothScrollArea
from .manga_card import MangaCard, FullMangaCard
from models import Manga
from directories import *
        
 
class MangaDashboard(SmoothScrollArea):
    def __init__(self, mc_width: int=295, mc_height: int=550, parent=None):
        super().__init__(parent)
        
        self.add_manga_button = QPushButton("Add Manga", parent=self)
        self.add_manga_button.setFixedSize(100, 32)
        self.add_manga_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_manga_button.move(self.width() - self.add_manga_button.width() - 15, 10)
        
        self.fmc = FullMangaCard(parent=self)
        self.fmc.cover.clicked_l.connect(self.fmc.close)
        self.fmc.close()
        
        self.root_layout = QVBoxLayout()
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root_layout.setSpacing(20)
        self.root_layout.setContentsMargins(20, 40, 20, 40)
        
        self.root_widget = QWidget()
        self.root_widget.setLayout(self.root_layout)
        
        self.setWidget(self.root_widget)
        
        self.mcards: dict[str, MangaCard] = {}
        
        self.mc_width = mc_width
        self.mc_height = mc_height
        self.max_mc_num = self.width() // self.mc_width
        self.mc_num = 0
        
    def add_manga(self, manga: Manga):
        mc = MangaCard(manga, self.mc_width, self.mc_height)
        mc.image.clicked_l.connect(lambda manga=manga: self.fmc.set_manga(manga))
        mc.image.clicked_l.connect(self.fmc.show)
        
        self.mcards[manga.name] = mc
        self._add_card_to_layout(mc)
        return mc
    
    def _add_card_to_layout(self, mc: MangaCard):
        if self.mc_num % self.max_mc_num == 0:  # if the current row is full
            new_layout = QHBoxLayout()
            new_layout.addWidget(mc)
            self.root_layout.addWidget(Separator())
            self.root_layout.addLayout(new_layout)
        else:
            self.root_layout.itemAt(self.root_layout.count() - 1).addWidget(mc)

        self.mc_num += 1
        
    def update_cards_layout(self):
        self.max_mc_num = self.width() // self.mc_width
        self.mc_num = 0
        self.root_layout.deleteLater()
        self.root_layout = QVBoxLayout()
        for mc in self.mcards.values():
            self._add_card_to_layout(mc)
        self.setLayout(self.root_layout)
    
    def update_manga(self, manga: Manga):
        mc: MangaCard = self.mcards[manga.name]
        if manga.current_chapter != 1 and manga.current_chapter != manga.last_chapter:
            if mc.chapter_buttons.get('current'):
                mc.chapter_buttons['current'][1].setText(f"Chapter {manga.current_chapter}")
                mc.chapter_buttons['current'][0].clicked.disconnect()
                mc.chapter_buttons['current'][0].clicked.connect(lambda _: mc.chapter_clicked.emit(manga.name, manga.current_chapter))
            else:
                mc.add_chapter_button(manga.current_chapter, manga._chapters_data[manga.current_chapter].name, manga._chapters_data[manga.current_chapter].upload_date, 'current', 3)
        
    def resizeEvent(self, arg__1):
        self.add_manga_button.move(self.width() - self.add_manga_button.width() - 15, 10)
        self.root_widget.setFixedSize(self.size())
        self.fmc.update_geometry()
        self.update_cards_layout()              # TODO: Might cause optimization issues, not work man sad :(
        return super().resizeEvent(arg__1)
        