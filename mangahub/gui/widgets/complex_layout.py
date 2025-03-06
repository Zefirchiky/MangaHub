from __future__ import annotations
from enum import auto

from PySide6.QtWidgets import (
    QWidget,
    QLayout, QStackedLayout, QVBoxLayout, QHBoxLayout
    )

    
class LayoutType:
    HORIZONTAL = auto()
    VERTICAL = auto()
    STACKED = auto()
    
class ComplexLayout:
    Type = LayoutType()
    
    def __init__(self, name: str='main', layout_type: LayoutType=Type.HORIZONTAL, parent=None):
        match layout_type:
            case LayoutType.HORIZONTAL | 'h' | 'H':
                layout = QHBoxLayout()
            case LayoutType.VERTICAL | 'v' | 'V':
                layout = QVBoxLayout()
            case LayoutType.STACKED | 's' | 'S':
                layout = QStackedLayout()
                
        self.name = name
        self.main_layout = layout
        self.layouts = {}
        self.widget: QWidget = None
        
    def add(self, name: str=None, parent: str=None, type_: LayoutType=Type.HORIZONTAL) -> 'ComplexLayout':
        layout = ComplexLayout(name, type_, parent=parent or self.main_layout)
        self.layouts[name] = layout
        return layout
    
    def delete(self, name: str):
        layout: QLayout = self.layouts.get(name)
        if layout is not None:
            layout.setParent(None)
            del self.layouts[name]
            layout.deleteLater()
        else:
            raise ValueError(f"Layout '{name}' not found")
    
    def get(self, name: str=None) -> QLayout:
        if name is None:
            return self.main_layout
        
        layout = self.layouts.get(name)
        if layout is not None:
            return layout
        else:
            raise ValueError(f"Layout '{name}' not found")
        
    def add_widget(self, widget: QWidget):
        self.main_layout.addWidget(widget)
        
    def set_parent(self, parent: str | QWidget | ComplexLayout):
        if isinstance(parent, QWidget):
            self.main_layout.setParent(parent)

        if isinstance(parent, str):
            parent = self.get(parent)
        parent.add_layout(self)
        
    def get_widget(self) -> QWidget:
        if self.widget:
            return self.widget
        
        self.widget = QWidget()
        self.widget.setLayout(self.main_layout)
        return self.widget
    
    def is_nested(self) -> bool:
        return self.layouts != {}

    def __iter__(self) -> list['ComplexLayout']:
        return iter(self.layouts.values())
