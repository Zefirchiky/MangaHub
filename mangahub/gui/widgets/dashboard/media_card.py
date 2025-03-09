from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from ..buttons import ChapterButton
from ..image import ImageWidget
from ..scroll_areas import LineLabel


class MediaCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setObjectName("MediaCard")
        self.setStyleSheet('''#MediaCard {
            background-color: #222222; 
            border-radius: 10px;
            border: 1px solid #444444;
            }''')        
        
        self.cover = ImageWidget()
        self.cover.set_placeholder(width=256, height=384)
        
        self.name_label = LineLabel()
        self.name_label.setFixedWidth(256)
        self.name_label.set_font(font_name='Arial', font_size=18, font_weight=75)
        
        self.top_button = ChapterButton().add_eye()
        self.mid_button = ChapterButton().add_eye()
        self.btm_button = ChapterButton().add_eye()
        
        self.root = QVBoxLayout()
        self.root.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.root.addWidget(self.cover)
        self.root.addWidget(self.name_label)
        self.root.addWidget(self.top_button)
        self.root.addWidget(self.mid_button)
        self.root.addWidget(self.btm_button)
        
        self.setLayout(self.root)
        
        self.name = ''
        
    def set_cover(self, img: ImageWidget.ImageType):
        self.cover.set_image(img)
        return self
    
    def set_name(self, name: str):
        self.name_label.set_text(name)
        self.name = name
        return self
        
    def set_date(self, date: str):
        pass
    
