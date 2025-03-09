from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from ..flow_layout import FlowLayout
from ..scroll_areas import SmoothScrollArea
from .media_card import MediaCard


class Dashboard(SmoothScrollArea):
    def __init__(self, mc_w_padding=20, mc_h_padding=20, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.root_layout = FlowLayout(spacing=10)
        self.root = QWidget()
        self.root.setContentsMargins(10, 10, 10, 10)
        self.root.setLayout(self.root_layout)
        self.setWidget(self.root)
        
        self.mc_w_padding = mc_w_padding
        self.mc_h_padding = mc_h_padding
        
        self.max_mc_in_row = 0
        self.mc_repo = {}
    
    def add_card(self, mc: MediaCard):
        self.root_layout.addWidget(mc)
        self.mc_repo[mc.name] = mc
        return self
        
    def delete_card(self, mc: MediaCard):
        try:
            del self.mc_repo[mc.name]
        except IndexError:
            pass
        
    def resizeEvent(self, arg__1):
        return super().resizeEvent(arg__1)