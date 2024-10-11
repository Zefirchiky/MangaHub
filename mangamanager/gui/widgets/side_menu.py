from PySide6.QtWidgets import (
    QWidget, QFrame,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve

from .separators import Separator
from .svg import SvgIcon


class SideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        bg_color = self.palette().color(self.backgroundRole())
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color.name()};
                border-right: 1px solid gray;
            }}
        """)

        self.parent = parent

        self._width = 72
        self.hidden_x = -self._width + 1
        self.visible_x = 0

        self.buttons = {}
        
        self.is_visible = False
        self.is_fully_opened = False
        self.checked_button = None
        self.current_x = self.hidden_x

        # menu
        menu_button = QPushButton()
        menu_button.setStyleSheet('''QPushButton {
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
        menu_button.setIcon(SvgIcon("mangamanager/resources/icons/menu-outline.svg").get_icon('white', fill='white'))

        menu_button.clicked.connect(lambda: self.handle_full_menu())

        menu_button_layout = QVBoxLayout()
        menu_button_layout.addWidget(menu_button)

        # buttons
        self.buttons_layout = QVBoxLayout()

        # settings
        settings_button = QPushButton()
        settings_button.setFixedHeight(56)
        settings_button.setIconSize(QSize(32, 32))
        settings_button.setIcon(SvgIcon("mangamanager/resources/icons/settings-outline.svg").get_icon('gray'))

        settings_button_layout = QVBoxLayout()
        settings_button_layout.addWidget(settings_button)

        # root layout
        root_layout = QVBoxLayout()
        root_layout.setSpacing(10)

        root_layout.addLayout(menu_button_layout)
        root_layout.addWidget(Separator())
        root_layout.addLayout(self.buttons_layout)
        root_layout.addStretch(2)
        root_layout.addWidget(Separator())
        root_layout.addLayout(settings_button_layout)
        self.setLayout(root_layout)

        # animations
        self.open_close_animation = QPropertyAnimation(self, b"geometry")
        self.open_close_animation.setDuration(300)
        self.open_close_animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.full_open_close_animation = QPropertyAnimation(self, b"geometry")
        self.full_open_close_animation.setDuration(300)
        self.full_open_close_animation.setEasingCurve(QEasingCurve.OutCubic)

    def handle_full_menu(self):
        self.is_fully_opened ^= 1
        if self.is_fully_opened:
            self._width = 150
        else:
            self._width = 72
            
        for button in self.buttons.keys():
            self.buttons[button]["button"].setText("  " + button if self.is_fully_opened else '')

        self.full_open_close_animation.setStartValue(self.geometry())
        self.full_open_close_animation.setEndValue(QRect(self.current_x, 0, self._width, self.parent.geometry().height()))
        self.full_open_close_animation.start()

        self.hidden_x = -self._width + 1
        self.adjust_geometry()

    def add_button(self, svg_icon=None, text=None):
        button = QPushButton()
        button.setCheckable(True)
        button.setFixedHeight(56)
        button.setFont(QFont("Times", 12, 2))
        button.setStyleSheet("color: white;")
        button_index = len(self.buttons)
        self.buttons[text] = {
            "button": button,
            "icon": svg_icon
        }

        if not self.checked_button:
            self.checked_button = button_index

        button.clicked.connect(lambda: self.change_checked_button(button_index))

        if svg_icon:
            button.setIconSize(QSize(32, 32))
            button.setIcon(svg_icon.get_icon('grey'))

        self.buttons_layout.addWidget(button)

    def change_checked_button(self, button_index):
        self.checked_button = button_index
        button_keys = [button for button in self.buttons.keys()]
        color = None
        is_checked = None

        for i in range(len(button_keys)):
            if i != button_index:
                is_checked = False
                color = 'gray'
            else:
                is_checked = True
                color = 'white'

            button = self.buttons[button_keys[i]]
            button["button"].setChecked(is_checked)
            button["button"].setIcon(button["icon"].get_icon(color))

    def adjust_geometry(self):
        if self.parent:
            parent_geometry = self.parent.geometry()
            self.setGeometry(self.current_x, 0, self._width, parent_geometry.height())

    def show_menu(self):
        if not self.is_visible:
            self.is_visible = True
            self.current_x = self.visible_x
            self.open_close_animation.setStartValue(self.geometry())
            self.open_close_animation.setEndValue(QRect(self.visible_x, 0, self._width, self.parent.geometry().height()))
            self.open_close_animation.start()

    def hide_menu(self):
        if self.is_visible:
            self.is_visible = False
            self.current_x = self.hidden_x
            self.open_close_animation.setStartValue(self.geometry())
            self.open_close_animation.setEndValue(QRect(self.hidden_x, 0, self._width, self.parent.geometry().height()))
            self.open_close_animation.start()
    