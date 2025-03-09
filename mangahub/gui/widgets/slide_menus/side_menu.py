from PySide6.QtCore import (QEasingCurve, QParallelAnimationGroup,
                            QPropertyAnimation, QRect, QSize, Qt)
from PySide6.QtGui import QCursor, QFont
from PySide6.QtWidgets import (QFrame, QGraphicsOpacityEffect, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QVBoxLayout)

from ..separators import Separator
from ..svg_icon import IconRepo, SVGIcon
from config import CM


class SideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._width = 72
        self.hidden_x = -self._width + 2
        self.visible_x = 0
        self.y_offset = 1
        self.current_x = self.hidden_x
        
        self.opened_state = False
        self.is_fully_opened = False
        self.checked_button = None

        self.buttons = {}


        # Menu
        menu_button = QPushButton()
        menu_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        menu_button.setStyleSheet('''
                                QPushButton {
                                    background-color: transparent;
                                    border: none;
                                    border-radius: 5px;
                                }
                                QPushButton:hover {
                                    background-color: gray;
                                    border: white;
                                }
                                ''')
        menu_button.setFixedHeight(56)
        menu_button.setIconSize(QSize(40, 40))
        icon = IconRepo.get_icon(IconRepo.Icons.MENU)
        icon.pressed.connect(print)
        menu_button.setIcon(icon.get_pixmap(40, 40))
        menu_button.clicked.connect(lambda: self.handle_full_menu())

        # Buttons
        self.buttons_layout = QVBoxLayout()

        # Settings
        self.settings_button = QPushButton()
        self.settings_button.setCheckable(True)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setFixedHeight(56)
        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setIcon(IconRepo.get_icon(IconRepo.Icons.SETTINGS).get_pixmap(32, 32))
        self.settings_button.clicked.connect(self.change_settings_icon)

        # root layout
        root_layout = QVBoxLayout()
        root_layout.setSpacing(10)

        root_layout.addWidget(menu_button)
        root_layout.addWidget(Separator())
        root_layout.addStretch(1)
        root_layout.addLayout(self.buttons_layout)
        root_layout.addStretch(1)
        root_layout.addWidget(Separator())
        root_layout.addWidget(self.settings_button)

        self.setLayout(root_layout)

        # animations
        self.open_close_animation = QPropertyAnimation(self, b"geometry")
        self.open_close_animation.setDuration(300)
        self.open_close_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.full_open_close_animation = QPropertyAnimation(self, b"geometry")
        self.full_open_close_animation.setDuration(300)
        self.full_open_close_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def add_button(self, fn, svg_icon: SVGIcon | None=None, text=None, is_default=False):
        button_index = len(self.buttons)

        layout = QHBoxLayout()

        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0)

        text = QLabel(text) if text else None
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        text.setFont(QFont("Times", 12, 2))
        text.setGraphicsEffect(opacity_effect)
        
        if svg_icon:
            layout.addWidget(svg_icon)
        layout.addWidget(text)

        button = QPushButton()
        button.setCheckable(True)
        button.setFixedHeight(56)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setLayout(layout)
        button.setContentsMargins(1, 1, 0, 0)
        button.clicked.connect(fn)
        button.clicked.connect(lambda: self.change_checked_button(button_index))

        self.buttons[button_index] = {
            "button": button,
            "opacity_effect": opacity_effect,
        }

        if is_default:
            self.change_checked_button(button_index)

        self.buttons_layout.addWidget(button)

    def handle_full_menu(self):
        self.is_fully_opened ^= 1
        if self.is_fully_opened:
            self._width = 150
        else:
            self._width = 72

        self.full_open_close_animation.setStartValue(self.geometry())
        self.full_open_close_animation.setEndValue(QRect(self.current_x - 3, self.y_offset, self._width, self.parent.geometry().height() - self.y_offset))
        self.full_open_close_animation.start()
        self.set_buttons_text()

        self.hidden_x = -self._width + 1

    def show_menu(self):
        if self.opened_state != 2:
            self.opened_state = 2
            self.current_x = self.visible_x
            self.open_close_animation.setStartValue(self.geometry())
            self.open_close_animation.setEndValue(QRect(self.current_x - 3, self.y_offset, self._width, self.parent.geometry().height() - self.y_offset))
            self.open_close_animation.start()

    def show_half_menu(self):
        if self.opened_state != 1:
            self.opened_state = 1
            self.current_x = self.visible_x
            self.open_close_animation.setStartValue(self.geometry())
            self.open_close_animation.setEndValue(QRect(10 - self._width, self.y_offset, self._width, self.parent.geometry().height() - self.y_offset))
            self.open_close_animation.start()

    def hide_menu(self):
        if self.opened_state:
            self.opened_state = False
            self.current_x = self.hidden_x
            self.open_close_animation.setStartValue(self.geometry())
            self.open_close_animation.setEndValue(QRect(self.current_x, self.y_offset, self._width, self.parent.geometry().height() - self.y_offset))
            self.open_close_animation.start()

    def set_buttons_text(self):
        self.anim_group = QParallelAnimationGroup()
        
        for button in self.buttons.keys():
            fade_animation = QPropertyAnimation(self.buttons[button]["opacity_effect"], b"opacity")
            fade_animation.setDuration(50)
            fade_animation.setStartValue(0 if self.is_fully_opened else 1)
            fade_animation.setEndValue(1 if self.is_fully_opened else 0)
            self.anim_group.addAnimation(fade_animation)

        self.anim_group.start()

    def change_checked_button(self, button_index):
        self.checked_button = button_index
        is_checked = None

        for i in self.buttons.keys():
            is_checked = i == button_index
            self.buttons[i]["button"].setChecked(is_checked)

    def change_settings_icon(self):
        if self.settings_button.isChecked():
            self.settings_button.setIcon(IconRepo.get_icon(IconRepo.Icons.SETTINGS).set_color(CM().highlight).get_pixmap(32, 32))
        else:
            self.settings_button.setIcon(IconRepo.get_icon(IconRepo.Icons.SETTINGS).get_pixmap(32, 32))

    def set_settings_function(self, fn):
        self.settings_button.clicked.connect(fn)

    def adjust_geometry(self):
        if self.parent:
            parent_geometry = self.parent.geometry()
            self.setGeometry(self.current_x - 3, self.y_offset, self._width, parent_geometry.height() - self.y_offset)

    