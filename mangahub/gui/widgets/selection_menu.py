from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QGraphicsOpacityEffect,
    QWidget, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, QSize, QRect, QPropertyAnimation, QEasingCurve

from .svg import SvgIcon
from .scroll_areas import SmoothScrollArea
from directories import ICONS_DIR


class AddElement(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedSize(80, 20)
        self.setIconSize(QSize(16, 16))
        self.setIcon(SvgIcon(ICONS_DIR / "plus.svg").get_icon('white'))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet('''
                            background-color: transparent;
                            border: 2px dashed grey;
                            border-radius: 5px;
                            ''')
        

class AddElementList(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(80, 20)
        self.setIconSize(QSize(16, 16))
        self.setIcon(SvgIcon(ICONS_DIR / "plus.svg").get_icon('white'))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet('''
                            background-color: transparent;
                            border: 2px dashed grey;
                            border-radius: 5px;
                            ''')


class SelectionElement(QPushButton):
    def __init__(self, parent=None, 
                 text="Text", icon: SvgIcon=None,
                 bg_color=None, border_color=None, text_color="white", icon_color="white"):
        super().__init__(parent)
        
        if not bg_color:
            bg_color = self.palette().window().color().name()
        
        if not border_color:
            border_color = self.palette().window().color().darker().name()
        
        self.setFixedSize(80, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet(f'''
                           background-color: {bg_color};
                           border: 2px solid {border_color};
                           border-radius: 5px;
                           color: {text_color};
                           ''')
        
        if icon:
            self.setIconSize(QSize(16, 16))
            self.setIcon(icon.get_icon(icon_color))
            
        self.setText(text)
        
        
class SelectionMenu(SmoothScrollArea):
    def __init__(self, parent=None, width=300, height=32):
        super().__init__(parent, vertical=False, bar=False)
        
        self.setFixedSize(width, height)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        self.current_x = 5
        self.add_element_widget = AddElement()
        self.add_element_widget.clicked.connect(lambda _: self.add_element(text=str(self.current_x)))
                
        self.root_layout = QHBoxLayout()
        self.root_layout.setContentsMargins(5, 5, 5, 5)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.root_layout.setSpacing(5)
        
        self.root_layout.addWidget(self.add_element_widget)
        
        self.root = QWidget()
        self.root.setLayout(self.root_layout)
        self.setWidget(self.root)
        
        self.add_element_animation = QPropertyAnimation(self.add_element_widget, b"geometry")
        self.add_element_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.add_element_animation.setDuration(75)
        
        self.selection_elements = {}
        
    def add_element(self, text="Text", icon=None, bg_color=None, border_color=None, text_color="white", icon_color="white") -> SelectionElement:
        graphics_effect = QGraphicsOpacityEffect()
        graphics_effect.setOpacity(0)
        selection_element = SelectionElement(text=text, icon=icon, bg_color=bg_color, border_color=border_color, text_color=text_color, icon_color=icon_color)
        selection_element.clicked.connect(lambda _: self.remove_element(text))
        selection_element.setGraphicsEffect(graphics_effect)
        
        self.current_x += selection_element.width() + 5
        

        self.add_element_animation.stop()
        self.add_element_animation.setStartValue(self.add_element_widget.geometry())
        self.add_element_animation.setEndValue(QRect(self.current_x, self.add_element_widget.geometry().y(), self.add_element_widget.width(), self.add_element_widget.height()))
        self.add_element_animation.finished.connect(lambda: self.root_layout.insertWidget(self.root_layout.count() - 1, selection_element))
        self.add_element_animation.start()
        
        self.selection_elements[text] = selection_element
        return selection_element
    
    def remove_element(self, text):
        self.root_layout.removeWidget(self.selection_elements[text])
        self.selection_elements[text].deleteLater()
        self.current_x -= self.selection_elements[text].width() + 5
        del self.selection_elements[text]
        
        
        self.add_element_animation.stop()
        self.add_element_animation.setStartValue(self.add_element_widget.geometry())
        self.add_element_animation.setEndValue(QRect(self.current_x, self.add_element_widget.geometry().y(), self.add_element_widget.width(), self.add_element_widget.height()))
        self.add_element_animation.start()
