from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton, QLabel
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

from gui.widgets import Separator

from models.abstract import AbstractChapter


class ChapterButton(QPushButton):
    clicked_ = Signal(AbstractChapter)
    
    def __init__(self, chapter: AbstractChapter=None, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        
        self.chapter = chapter
        
        self.language_label = None
        
        self.chapter_label = QLabel()
        self.chapter_label.setContentsMargins(0, 0, 0, 0)
        self.chapter_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.date_label = QLabel()   # f"{upload_date.split('T')[0] if upload_date else ''}"
        self.date_label.setFont(QFont("Times", 8, 5))
        self.date_label.setStyleSheet("color: gray;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(5, 0, 5, 0)
        self.root_layout.addWidget(self.chapter_label)
        
        self.setLayout(self.root_layout)
        
        if chapter:
            self.set_chapter(chapter)
        
    def set_chapter(self, chapter: AbstractChapter) -> 'ChapterButton':
        self.chapter = chapter
        
        if self.language_label and self.language_label.text() == '':
            self.language_label.setText(chapter.language)
        
        text = f"Chapter {chapter.number}"
        if chapter.name:
            text += f": {chapter.name}"
        self.chapter_label.setText(text)
        
        if chapter.upload_date:
            upload_date = f"{chapter.upload_date.split('T')[0] if chapter.upload_date else ''}"
            self.date_label.setText(upload_date)
        
        self.clicked.connect(lambda _: self.clicked_.emit(self.chapter))
            
        return self
    
    def add_language(self, language: str=None) -> 'ChapterButton':
        if language:
            self.language_label = QLabel(language)
            self.root_layout.insertWidget(0, self.language_label)
            self.root_layout.insertWidget(1, Separator())
        return self