from __future__ import annotations
from typing import Union

from loguru import logger
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QColor

ColorType = Union[str, QColor]

class Color(QColor):
    color_type = ColorType
    
    def __init__(self, color: str | QColor, 
                 hover_color: str | QColor | None=None,
                 pressed_color: str | QColor | None=None):
        super().__init__(color)
        self.hover = hover_color
        self.pressed = pressed_color
        
    def set_hover(self, color):
        self.hover = color
        return self
    
    def set_pressed(self, color):
        self.pressed = color
        return self

class CM(QObject):
    '''Color Manager class to manage the color of the application.
    Use CM() to access the instance of this class.'''
    _instance: CM | None = None
    _initialized = False
    sys_color_changed = Signal(str)
    
    transparent = QColor(Qt.GlobalColor.transparent)
    
    color_type = ColorType
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, app=None):
        # Only initialize if this is a new instance
        if not self._initialized:
            super().__init__()
            self._initialized = True
            
            self.app = app
            qApp.paletteChanged.connect(self.sys_color_changed.emit)
            self.sys_color_changed.connect(self._update_highlight)
            
            self.theme = None
            self.set_theme()
            self.highlight = QColor(self.theme['highlight']['color'] or qApp.palette().highlight().color())
            self.bg = QColor(self.theme['background']['color'] or qApp.palette().highlight().color())
            self.widget_bg = QColor(self.theme['widget_bg']['color'] or qApp.palette().base().color())
            self.widget_border = QColor(self.theme['widget_border']['color'] or qApp.palette().highlight().color())
            self.widget_bg_alt = QColor(self.theme['widget_bg_alt']['color'] or qApp.palette().alternateBase().color())
            self.widget_border_alt = QColor(self.theme['widget_border_alt']['color'] or qApp.palette().highlight().color())
            self.icon = QColor(self.theme['icon_color']['color'] or qApp.palette().text().color())
            self.text = QColor(self.theme['text_color']['color'] or qApp.palette().text().color())
            
            logger.success("Color Manager initialized")
    
    def _update_highlight(self):
        if self.theme['highlight']['color'] is None:
            self.highlight = qApp.palette().highlight().color().name()  # noqa: F821
        return self
    
    def set_theme(self, theme=None): # WIP
        self.theme = {
            'highlight': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'background': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'widget_bg': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'widget_border': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'widget_bg_alt': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'widget_border_alt': {
                'color': None,
                'hover': None,
                'pressed': None
            },
            'icon_color': {
                'color': 'white',
                'hover': None,
                'pressed': None
            },
            'text_color': {
                'color': None,
                'hover': None,
                'pressed': None
            }
        }
        return self