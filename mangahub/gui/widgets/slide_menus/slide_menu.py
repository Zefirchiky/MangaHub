from PySide6.QtWidgets import (
    QFrame,
    QBoxLayout,
    QPushButton
)
from PySide6.QtCore import (
    Qt, QRect, QSize,
    QPropertyAnimation, QEasingCurve)
from PySide6.QtGui import QCursor

from ..separators import Separator
from ..svg import SvgIcon
from directories import ICONS_DIR


class SlideMenu(QFrame):
    def __init__(self, parent=None, is_vertical=True, menu_expand_button_pos=0):
        super().__init__(parent)
        self.parent = parent

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAutoFillBackground(True)

        self.menu_expand_button_pos = menu_expand_button_pos

        self.is_opened = False
        self.checked_button = None

        self.buttons = {}
        self.buttons_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom if is_vertical else QBoxLayout.Direction.LeftToRight)

        expand_button_icon = SvgIcon(f"{ICONS_DIR}/menu.svg")

        expansion_button = QPushButton()
        expansion_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        expansion_button.setStyleSheet('''QPushButton { background-color: transparent; border: none; border-radius: 5px; }''')
        expansion_button.setIconSize(QSize(16, 16))
        expansion_button.setIcon(expand_button_icon.get_icon('white'))

        self.root = QBoxLayout(QBoxLayout.Direction.TopToBottom if is_vertical else QBoxLayout.Direction.LeftToRight)

        if not menu_expand_button_pos:
            self.root.addWidget(expansion_button)
        self.root.addWidget(Separator())
        self.root.addLayout(self.buttons_layout)

    def adjust_geometry_with_animation(self, geom1: QRect, geom2: QRect, 
                                       anim_time=1000, easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
                                       fn_at_animation=None, fn_after_animation=None):
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(anim_time)
        self.geometry_animation.setEasingCurve(easing)

        if fn_at_animation:
            self.geometry_animation.valueChanged.connect(fn_at_animation)
        if fn_after_animation:
            self.geometry_animation.finished.connect(fn_after_animation)

        self.geometry_animation.setStartValue(geom1)
        self.geometry_animation.setEndValue(geom2)
        self.geometry_animation.start()

    def get_geometry(self, x=0, y=0, width=0, height=0):
        if self.parent and not (width == 0 and height == 0):
            parent_geometry = self.parent.geometry()
            if not height:
                height = parent_geometry.height()
            if not width:
                width = parent_geometry.width()
        
        else:
            print("Error: parent not found.")

        return QRect(x, y, width, height)