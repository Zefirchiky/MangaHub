from PySide6.QtWidgets import QLayout, QLayoutItem
from PySide6.QtCore import QRect, QSize, Qt, QPoint


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._items: list[QLayoutItem] = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self._items.append(item)
        self.invalidate()

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self.invalidate()
            return item
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    # Calculate the preferred size hint of the layout
    def sizeHint(self) -> QSize:
        # A good sizeHint for a FlowLayout often considers the parent's width
        # or a reasonable default to calculate the height.
        # If no parent, it might default to its minimum size.
        if self.parentWidget():
            width = self.parentWidget().width()-2
            # Ensure width is at least the minimum required width for layout
            width = max(width, self.minimumSize().width())
            height = self.heightForWidth(width)
            return QSize(width, height)
        else:
            return self.minimumSize()

    # Calculate the minimum size required by the layout
    def minimumSize(self):
        if not self._items:
            margins = self.contentsMargins()
            return QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

        max_item_width = max([item.sizeHint().width() for item in self._items if item.widget()])
        
        margins = self.contentsMargins()
        # Minimum content width: just enough for the widest item
        min_content_width = max_item_width
        
        min_width_with_margins = min_content_width + margins.left() + margins.right()
        
        # Calculate the minimum height at this minimum width
        min_height = self.heightForWidth(min_width_with_margins)

        return QSize(min_width_with_margins, min_height)

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        spacing = self.spacing() if self.spacing() != -1 else 0

        effective_rect = rect.adjusted(
            margins.left(), margins.top(), -margins.right(), -margins.bottom()
        )

        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._items:
            item_size = item.sizeHint()
            item_width = item_size.width()
            item_height = item_size.height()

            if x + item_width > effective_rect.right():
                x = effective_rect.x()
                y += line_height + spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))

            x += item_width + spacing
            line_height = max(line_height, item_height)
        
        total_height = y + line_height - rect.y() + margins.bottom()
        return total_height
