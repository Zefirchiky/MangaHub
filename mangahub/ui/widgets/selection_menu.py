from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QStyle,
    QSizePolicy,
)

from .scroll_areas import SmoothScrollArea
from .svg_icon import SVGIcon, IconRepo
from ui.widgets import FlowLayout


class AddElement(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(80, 20)
        self.setIconSize(QSize(16, 16))
        self.setIcon(IconRepo.get(IconRepo.Icons.ADD).get_qicon())
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
                            background-color: transparent;
                            border: 2px dashed grey;
                            border-radius: 5px;
                            """)


class SelectionElement(QPushButton):
    def __init__(
        self,
        parent=None,
        text="Text",
        icon: SVGIcon | IconRepo.Icons | None = None,
        bg_color=None,
        border_color=None,
        text_color="white",
        icon_color="white",
    ):
        super().__init__(parent)

        if not bg_color:
            bg_color = self.palette().window().color().name()

        if not border_color:
            border_color = self.palette().window().color().darker().name()

        self.setFixedSize(80, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(f"""
                           background-color: {bg_color};
                           border: 2px solid {border_color};
                           border-radius: 5px;
                           color: {text_color};
                           """)

        if icon:
            self.setIconSize(QSize(16, 16))
            self.setIcon(icon.get_icon(icon_color).get_qicon())

        self.setText(text)


class SelectionMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Panel)

        self.setMinimumWidth(400)
        self.setMaximumWidth(500)

        self.add_element_button = AddElement()
        self.add_element_button.clicked.connect(
            lambda: self.add_element(SelectionElement())
        )

        self.root_layout = FlowLayout(margin=5, spacing=3)
        self.root_layout.addWidget(self.add_element_button)
        self.setLayout(self.root_layout)

        self.selection_elements: list[SelectionElement] = []

        self.adjustSize()

    def add_element(self, element: SelectionElement):
        element.clicked.connect(
            lambda: self._element_clicked(self.root_layout.count() - 2)
        )
        self.selection_elements.append(element)
        self.root_layout.addWidget(element)
        self.adjustSize()

    def _element_clicked(self, i):
        el = self.selection_elements.pop(i)
        self.root_layout.takeAt(i+1)
        el.deleteLater()
        print(self.width())
        self.adjustSize()
        print(self.width())
