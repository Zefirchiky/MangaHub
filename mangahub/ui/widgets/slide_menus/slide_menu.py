from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QBoxLayout, QFrame, QPushButton
from loguru import logger

from ..separators import Separator
from ..svg_icon import IconRepo



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

        expand_button_icon = IconRepo.get(IconRepo.Icons.MENU)

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

    def adjust_geometry_with_animation(self, geom1: QRect | list | tuple, geom2: QRect | list | tuple, 
                                       anim_time=300, easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
                                       fn_at_animation=None, fn_after_animation=None):
        if isinstance(geom1, (list, tuple)):
            geom1 = QRect(*geom1)
        if isinstance(geom2, (list, tuple)):
            geom2 = QRect(*geom2)
            
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
            logger.error("Can't get parent geometry")

        return QRect(x, y, width, height)