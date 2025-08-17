from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
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
        
        # FIXED: Remove Fixed size policy, use Preferred instead
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.setMinimumWidth(400)
        self.setMaximumWidth(500)

        self.add_element_button = AddElement()
        self.add_element_button.clicked.connect(
            lambda: self.add_element(SelectionElement(text=f"Item {len(self.selection_elements) + 1}"))
        )

        # Assuming FlowLayout is available
        self.root_layout = FlowLayout(margin=5, h_spacing=3)
        self.root_layout.addWidget(self.add_element_button)
        self.setLayout(self.root_layout)

        self.selection_elements: list[SelectionElement] = []

    def add_element(self, element: SelectionElement):
        element.clicked.connect(
            lambda checked=False, idx=len(self.selection_elements): self._element_clicked(idx)
        )
        self.selection_elements.append(element)
        self.root_layout.addWidget(element)
        
        # Optional: Force geometry update (usually not needed with Preferred policy)
        self.updateGeometry()
        
    def _element_clicked(self, i):
        if i < len(self.selection_elements):
            el = self.selection_elements.pop(i)
            # Find the actual widget index in the layout (accounting for the add button)
            widget_index = i + 1  # +1 because add_element_button is at index 0
            self.root_layout.takeAt(widget_index)
            el.deleteLater()
            
            # Update the click handlers for remaining elements
            for j, element in enumerate(self.selection_elements):
                element.clicked.disconnect()
                element.clicked.connect(
                    lambda checked=False, idx=j: self._element_clicked(idx)
                )
            
            self.updateGeometry()